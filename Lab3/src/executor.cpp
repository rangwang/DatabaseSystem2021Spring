/**
 * @author Zhaonian Zou <znzou@hit.edu.cn>,
 * School of Computer Science and Technology,
 * Harbin Institute of Technology, China
 */

#include "executor.h"

#include <exceptions/buffer_exceeded_exception.h>
#include <cmath>
#include <ctime>
#include <functional>
#include <iostream>
#include <string>
#include <utility>

#include "file_iterator.h"
#include "page_iterator.h"
#include "storage.h"

using namespace std;

namespace badgerdb
{

  void TableScanner::print() const
  {
    badgerdb::File file = badgerdb::File::open(tableFile.filename());
    for (badgerdb::FileIterator iter = file.begin(); iter != file.end(); ++iter)
    {
      badgerdb::Page page = *iter;
      badgerdb::Page *buffered_page;
      bufMgr->readPage(&file, page.page_number(), buffered_page);

      for (badgerdb::PageIterator page_iter = buffered_page->begin();
           page_iter != buffered_page->end(); ++page_iter)
      {
        string key = *page_iter;
        string print_key = "(";
        int current_index = 0;
        for (int i = 0; i < tableSchema.getAttrCount(); ++i)
        {
          switch (tableSchema.getAttrType(i))
          {
          case INT:
          {
            int true_value = 0;
            for (int j = 0; j < 4; ++j)
            {
              if (std::string(key, current_index + j, 1)[0] == '\0')
              {
                continue; // \0 is actually representing 0
              }
              true_value +=
                  (std::string(key, current_index + j, 1))[0] * pow(128, 3 - j);
            }
            print_key += to_string(true_value);
            current_index += 4;
            break;
          }
          case CHAR:
          {
            int max_len = tableSchema.getAttrMaxSize(i);
            print_key += std::string(key, current_index, max_len);
            current_index += max_len;
            current_index +=
                (4 - (max_len % 4)) % 4; // align to the multiple of 4
            break;
          }
          case VARCHAR:
          {
            int actual_len = key[current_index];
            current_index++;
            print_key += std::string(key, current_index, actual_len);
            current_index += actual_len;
            current_index +=
                (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
            break;
          }
          }
          print_key += ",";
        }
        print_key[print_key.size() - 1] = ')'; // change the last ',' to ')'
        cout << print_key << endl;
      }
      bufMgr->unPinPage(&file, page.page_number(), false);
    }
    bufMgr->flushFile(&file);
  }

  JoinOperator::JoinOperator(File &leftTableFile,
                             File &rightTableFile,
                             const TableSchema &leftTableSchema,
                             const TableSchema &rightTableSchema,
                             const Catalog *catalog,
                             BufMgr *bufMgr)
      : leftTableFile(leftTableFile),
        rightTableFile(rightTableFile),
        leftTableSchema(leftTableSchema),
        rightTableSchema(rightTableSchema),
        resultTableSchema(
            createResultTableSchema(leftTableSchema, rightTableSchema)),
        catalog(catalog),
        bufMgr(bufMgr),
        isComplete(false)
  {
    // nothing
  }

  TableSchema JoinOperator::createResultTableSchema(
      const TableSchema &leftTableSchema,
      const TableSchema &rightTableSchema)
  {
    vector<Attribute> attrs;

    // first add all the left table attrs to the result table
    for (int k = 0; k < leftTableSchema.getAttrCount(); ++k)
    {
      Attribute new_attr = Attribute(
          leftTableSchema.getAttrName(k), leftTableSchema.getAttrType(k),
          leftTableSchema.getAttrMaxSize(k), leftTableSchema.isAttrNotNull(k),
          leftTableSchema.isAttrUnique(k));
      attrs.push_back(new_attr);
    }

    // test every right table attrs, if it doesn't have the same attr(name and
    // type) in the left table, then add it to the result table
    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      bool has_same = false;
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          has_same = true;
        }
      }
      if (!has_same)
      {
        Attribute new_attr = Attribute(
            rightTableSchema.getAttrName(i), rightTableSchema.getAttrType(i),
            rightTableSchema.getAttrMaxSize(i), rightTableSchema.isAttrNotNull(i),
            rightTableSchema.isAttrUnique(i));
        attrs.push_back(new_attr);
      }
    }
    return TableSchema("TEMP_TABLE", attrs, true);
  }

  void JoinOperator::printRunningStats() const
  {
    cout << "# Result Tuples: " << numResultTuples << endl;
    cout << "# Used Buffer Pages: " << numUsedBufPages << endl;
    cout << "# I/Os: " << numIOs << endl;
  }

  vector<Attribute> JoinOperator::getCommonAttributes(
      const TableSchema &leftTableSchema,
      const TableSchema &rightTableSchema) const
  {
    vector<Attribute> common_attrs;
    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          Attribute new_attr = Attribute(rightTableSchema.getAttrName(i),
                                         rightTableSchema.getAttrType(i),
                                         rightTableSchema.getAttrMaxSize(i),
                                         rightTableSchema.isAttrNotNull(i),
                                         rightTableSchema.isAttrUnique(i));
          common_attrs.push_back(new_attr);
        }
      }
    }
    return common_attrs;
  }

  /**
 * use the original key to generate the search key
 * @param key
 * @param common_attrs
 * @param TableSchema
 * @return
 */
  string construct_search_key(string key,
                              vector<Attribute> &common_attrs,
                              const TableSchema &TableSchema)
  {
    string search_key;
    int current_index = 0;
    int current_attr_index = 0;
    for (int i = 0; i < TableSchema.getAttrCount(); ++i)
    {
      switch (TableSchema.getAttrType(i))
      {
      case INT:
      {
        if (TableSchema.getAttrName(i) ==
                common_attrs[current_attr_index].attrName &&
            TableSchema.getAttrType(i) ==
                common_attrs[current_attr_index].attrType)
        {
          search_key += std::string(key, current_index, 4);
          current_attr_index++;
        }
        current_index += 4;
        break;
      }
      case CHAR:
      {
        int max_len = TableSchema.getAttrMaxSize(i);
        if (TableSchema.getAttrName(i) ==
                common_attrs[current_attr_index].attrName &&
            TableSchema.getAttrType(i) ==
                common_attrs[current_attr_index].attrType)
        {
          search_key += std::string(key, current_index, max_len);
          current_attr_index++;
        }
        current_index += max_len;
        current_index += (4 - (max_len % 4)) % 4;
        ; // align to the multiple of 4
        break;
      }
      case VARCHAR:
      {
        int actual_len = key[current_index];
        current_index++;
        if (TableSchema.getAttrName(i) ==
                common_attrs[current_attr_index].attrName &&
            TableSchema.getAttrType(i) ==
                common_attrs[current_attr_index].attrType)
        {
          search_key += std::string(key, current_index, actual_len);
          current_attr_index++;
        }
        current_index += actual_len;
        current_index +=
            (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
        break;
      }
      }
      if (current_attr_index >= common_attrs.size())
        break;
    }
    return search_key;
  }

  string JoinOperator::joinTuples(string leftTuple,
                                  string rightTuple,
                                  const TableSchema &leftTableSchema,
                                  const TableSchema &rightTableSchema) const
  {
    int cur_right_index = 0; // current substring index in the right table key
    string result_tuple = leftTuple;

    for (int i = 0; i < rightTableSchema.getAttrCount(); ++i)
    {
      bool has_same = false;
      for (int j = 0; j < leftTableSchema.getAttrCount(); ++j)
      {
        if ((leftTableSchema.getAttrType(j) == rightTableSchema.getAttrType(i)) &&
            (leftTableSchema.getAttrName(j) == rightTableSchema.getAttrName(i)))
        {
          has_same = true;
        }
      }
      // if the key is only owned by right table, add it to the result tuple
      switch (rightTableSchema.getAttrType(i))
      {
      case INT:
      {
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, 4);
        }
        cur_right_index += 4;
        break;
      }
      case CHAR:
      {
        int max_len = rightTableSchema.getAttrMaxSize(i);
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, max_len);
        }
        cur_right_index += max_len;
        unsigned align_ = (4 - (max_len % 4)) % 4; // align to the multiple of
                                                   // 4
        for (int k = 0; k < align_; ++k)
        {
          result_tuple += "0";
          cur_right_index++;
        }
        break;
      }
      case VARCHAR:
      {
        int actual_len = rightTuple[cur_right_index];
        result_tuple += std::string(rightTuple, cur_right_index, 1);
        cur_right_index++;
        if (!has_same)
        {
          result_tuple += std::string(rightTuple, cur_right_index, actual_len);
        }
        cur_right_index += actual_len;
        unsigned align_ =
            (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
        for (int k = 0; k < align_; ++k)
        {
          result_tuple += "0";
          cur_right_index++;
        }
        break;
      }
      }
    }
    return result_tuple;
  }

  bool OnePassJoinOperator::execute(int numAvailableBufPages, File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 0;
    numIOs = 0;

    // TODO: Execute the join algorithm

    isComplete = true;
    return true;
  }

  void getTuple(TableSchema tableSchema, Page p,
                vector<vector<string>> &records)
  {
    for (PageIterator pageIter = p.begin(); pageIter != p.end(); ++pageIter)
    {
      string record = *pageIter;
      int current_index = 0;
      vector<string> oneRecord;
      string attrs;
      for (int i = 0; i < tableSchema.getAttrCount(); ++i)
      {
        switch (tableSchema.getAttrType(i))
        {
        case INT:
        {
          int true_value = 0;
          for (int j = 0; j < 4; ++j)
          {
            if (std::string(record, current_index + j, 1)[0] == '\0')
            {
              continue; // \0 is actually representing 0
            }
            true_value += (std::string(record, current_index + j, 1))[0] *
                          pow(128, 3 - j);
          }
          attrs = to_string(true_value);
          oneRecord.push_back(attrs);
          current_index += 4;
          break;
        }
        case CHAR:
        {
          int max_len = tableSchema.getAttrMaxSize(i);
          attrs = std::string(record, current_index, max_len);
          oneRecord.push_back(attrs);
          current_index += max_len;
          current_index +=
              (4 - (max_len % 4)) % 4; // align to the multiple of 4
          break;
        }
        case VARCHAR:
        {
          int actual_len = record[current_index];
          current_index++;
          attrs = std::string(record, current_index, actual_len);
          oneRecord.push_back(attrs);
          current_index += actual_len;
          current_index +=
              (4 - ((actual_len + 1) % 4)) % 4; // align to the multiple of 4
          break;
        }
        }
      }
      // cout << oneRecord << endl;
      records.push_back(oneRecord);
    }
  }

  string createTupleFromString(TableSchema TableSchema, string joinTupleStr,
                               vector<DataType> dataTypes)
  {
    int attrNum = dataTypes.size();
    string result;
    int now_insert_i = 0;
    for (int attr = 0; attr < attrNum; ++attr)
    {
      DataType dataType = dataTypes[attr];
      string token;
      if (joinTupleStr.find(" ") != -1)
      {
        token = joinTupleStr.substr(0, joinTupleStr.find(" "));
        // cout << "token" << token << endl;
        joinTupleStr = joinTupleStr.substr(joinTupleStr.find(" ") + 1);
        // cout << "joinTuple" << joinTupleStr << endl;
      }
      else
      {
        token = joinTupleStr;
        // cout << token.size() << endl;
      }
      // cout << dataType << endl;
      switch (dataType)
      {
      case INT:
      {
        int value = atoi(token.c_str());
        for (int j = 0; j < 4; ++j)
        {
          char c = value;
          result.insert(now_insert_i, 1, c);
          // cout << "result" << result << endl;
          value = value >> 8;
        }
        now_insert_i += 4;
        break;
      }
      case CHAR:
      {
        int max_len = TableSchema.getAttrMaxSize(attr);
        result += token;
        now_insert_i += token.size();
        for (int j = 0; j < (max_len - token.size()); ++j)
        {
          result.insert(now_insert_i, 1, '0');
          // cout << "result" << result << endl;
          now_insert_i++;
        }
        // align length to the multiple of 4
        unsigned align_ = (4 - (max_len % 4)) % 4;
        for (int k = 0; k < align_; ++k)
        {
          result.insert(now_insert_i, 1, '0');
          // cout << "result" << result << endl;
          now_insert_i++;
        }
        break;
      }
      case VARCHAR:
      {
        unsigned true_len = token.size(); // assume -> 0< length < 128
        char len_2_char = true_len;
        result.insert(now_insert_i, 1, len_2_char);
        // cout << "result" << result << endl;
        now_insert_i++;
        result += token;
        now_insert_i += token.size();
        // align length to the multiple of 4
        unsigned align_ = (4 - ((true_len + 1) % 4)) % 4;
        // cout << align_ << endl;
        for (int k = 0; k < align_; ++k)
        {
          result.insert(now_insert_i, 1, '0');
          // cout << "result" << result << endl;
          now_insert_i++;
        }
        break;
      }
      }
    }
    return result;
  }

  bool NestedLoopJoinOperator::execute(int numAvailableBufPages,
                                       File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 1;
    numIOs = 0;
    // cout << "wrong at 303" << endl;
    // File leftFile = File(leftTableFile);
    // cout << "wrong at 304" << endl;
    // File rightFile = File(rightTableFile);
    cout << "numAvaliableBufPages : " << numAvailableBufPages << endl;
    Page *bufferBlocks[numAvailableBufPages] = {}; // 缓冲池
    // cout << "wrong at 306" << endl;
    FileIterator rightIter = rightTableFile.begin();
    // cout << "wrong at 313" << endl;
    while (rightIter != rightTableFile.end())
    {
      // cout << "wrong at 316" << endl;
      int i;
      for (i = 0;
           i < numAvailableBufPages - 1 && rightIter != rightTableFile.end();
           ++rightIter, ++i)
      { // 将磁盘中外关系的numAvailableBufBages -
        // 1个页取出放在缓冲池bufferBlocks中
        Page p = *rightIter;
        bufMgr->readPage(&rightTableFile, p.page_number(), bufferBlocks[i]);
        numUsedBufPages++;
        numIOs++;
      }
      cout << "numUsedBufPages: " << numUsedBufPages << endl;
      for (int j = 0; j < i; ++j)
      { // 分别取出外关系在缓冲池中的每一页
        vector<vector<string>> rightTuple;
        getTuple(rightTableSchema, *bufferBlocks[j],
                 rightTuple); // 分别取出每一页中的每一条元组
        cout << "rightTuple Size : " << rightTuple.size() << endl;
        int rightTupleNum = rightTuple.size(); // 外关系在该页中的元组个数

        for (
            FileIterator leftIter = leftTableFile.begin();
            leftIter != leftTableFile.end();
            ++leftIter)
        { // 对于内关系的每一条元组与外关系在缓冲池中的元组分别进行自然连接
          numIOs++;
          Page leftPage = *leftIter;
          // cout << "2" << endl;
          bufferBlocks[numAvailableBufPages - 1] =
              &leftPage; // 将内关系存储到缓冲池最后一页
          // cout << "3" << endl;
          // numUsedBufPages++;  // 使用的缓冲池页数加1
          vector<vector<string>> leftTuple;
          getTuple(leftTableSchema, *bufferBlocks[numAvailableBufPages - 1],
                   leftTuple); // 取出内关系一页的record
          cout << "leftTuple Size : " << leftTuple.size() << endl;
          // cout << "4" << endl;
          int leftTupleNum = leftTuple.size(); // 内关系一页的元组数量
          for (int r = 0; r < rightTupleNum; r++)
          {
            for (int l = 0; l < leftTupleNum; l++)
            {
              string joinTuple;
              int attr;
              vector<DataType> dataTypes;
              for (attr = 0; attr < resultTableSchema.getAttrCount(); ++attr)
              {
                // cout << "5" << endl;
                if (attr != 0)
                  joinTuple.append(" ");
                string joinAttr =
                    resultTableSchema.getAttrName(attr); // 两关系共有的属性
                dataTypes.push_back(resultTableSchema.getAttrType(attr));
                // cout << "6" << endl;
                if (leftTableSchema.hasAttr(joinAttr) &&
                    rightTableSchema.hasAttr(joinAttr))
                {
                  // cout << "7" << endl;
                  int leftPos = leftTableSchema.getAttrNum(joinAttr);
                  int rightPos = rightTableSchema.getAttrNum(joinAttr);
                  if (leftTuple[l][leftPos] == rightTuple[r][rightPos])
                    joinTuple.append(leftTuple[l][leftPos]);
                  else
                    break;
                }
                else if (leftTableSchema.hasAttr(joinAttr))
                {
                  int leftPos = leftTableSchema.getAttrNum(joinAttr);
                  joinTuple.append(leftTuple[l][leftPos]);
                }
                else if (rightTableSchema.hasAttr(joinAttr))
                {
                  int rightPos = rightTableSchema.getAttrNum(joinAttr);
                  joinTuple.append(rightTuple[r][rightPos]);
                }
              }
              if (attr == resultTableSchema.getAttrCount())
              {
                // cout << joinTuple << endl;
                string result = createTupleFromString(resultTableSchema,
                                                      joinTuple, dataTypes);
                HeapFileManager::insertTuple(result, resultFile, bufMgr);
                numResultTuples++;
              }
            }
          }
        }
      }
      isComplete = true;
      return true;
    }
  }

  BucketId GraceHashJoinOperator::hash(const string &key) const
  {
    std::hash<string> strHash;
    return strHash(key) % numBuckets;
  }

  bool GraceHashJoinOperator::execute(int numAvailableBufPages,
                                      File &resultFile)
  {
    if (isComplete)
      return true;

    numResultTuples = 0;
    numUsedBufPages = 0;
    numIOs = 0;

    // TODO: Execute the join algorithm

    isComplete = true;
    return true;
  }

} // namespace badgerdb