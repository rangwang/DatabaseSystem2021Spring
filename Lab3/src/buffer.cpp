/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University
 * of Wisconsin-Madison.
 */

#include "buffer.h"

#include <iostream>
#include <memory>

#include "exceptions/bad_buffer_exception.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/hash_not_found_exception.h"
#include "exceptions/invalid_page_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"

namespace badgerdb {

BufMgr::BufMgr(std::uint32_t bufs) : numBufs(bufs) {
  bufDescTable = new BufDesc[bufs];

  for (FrameId i = 0; i < bufs; i++) {
    bufDescTable[i].frameNo = i;
    bufDescTable[i].valid = false;
  }

  bufPool = new Page[bufs];

  int htsize = ((((int)(bufs * 1.2)) * 2) / 2) + 1;
  hashTable = new BufHashTbl(htsize);  // allocate the buffer hash table

  clockHand = bufs - 1;
}

BufMgr::~BufMgr() {
  for (FrameId i = 0; i < numBufs; i++) {
    if (bufDescTable[i].dirty) {
      bufDescTable[i].file->writePage(bufPool[i]);
    }
  }
  delete[] bufDescTable;
  delete[] bufPool;
  delete hashTable;
}

void BufMgr::advanceClock() { clockHand = (clockHand + 1) % numBufs; }

void BufMgr::allocBuf(FrameId& frame) {
  FrameId frameNo = 0;
  while (frameNo < numBufs * 2) {
    frameNo++;
    advanceClock();
    if (bufDescTable[clockHand].valid == false) {
      break;
    }
    if (bufDescTable[clockHand].refbit) {
      bufDescTable[clockHand].refbit = false;
      continue;
    }
    if (bufDescTable[clockHand].pinCnt > 0) {
      continue;
    }
    if (bufDescTable[clockHand].dirty) {
      bufDescTable[clockHand].file->writePage(bufPool[clockHand]);
    }
    hashTable->remove(bufDescTable[clockHand].file,
                      bufDescTable[clockHand].pageNo);
    break;
  }
  frame = bufDescTable[clockHand].frameNo;
  bufDescTable[clockHand].Clear();
}

void BufMgr::readPage(File* file, const PageId pageNo, Page*& page) {
  FrameId frameNo;
  try  // look up if the page is in the buffer pool
  {
    hashTable->lookup(file, pageNo, frameNo);
    bufDescTable[frameNo].refbit = true;
    bufDescTable[frameNo].pinCnt++;
  } catch (HashNotFoundException e) {
    allocBuf(frameNo);
    bufPool[frameNo] = file->readPage(pageNo);
    hashTable->insert(file, pageNo, frameNo);
    bufDescTable[frameNo].Set(file, pageNo);
  }
  page = &bufPool[frameNo];
}

void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) {
  FrameId frameNo;
  hashTable->lookup(file, pageNo, frameNo);
  if (dirty == true) {
    bufDescTable[frameNo].dirty = true;
  }
  if (bufDescTable[frameNo].pinCnt > 0) {
    bufDescTable[frameNo].pinCnt--;
  } else {
    throw PageNotPinnedException(file->filename(), pageNo, frameNo);
  }
}

void BufMgr::flushFile(const File* file) {
  for (FrameId i = 0; i < numBufs; i++) {
    if (bufDescTable[i].file == file) {
      if (bufDescTable[i].pinCnt > 0) {
        throw PagePinnedException(file->filename(), bufDescTable[i].pageNo, i);
      }
      if (!bufDescTable[i].valid) {
        throw BadBufferException(bufDescTable[i].frameNo, bufDescTable[i].dirty,
                                 bufDescTable[i].valid, bufDescTable[i].refbit);
      }
      if (bufDescTable[i].dirty) bufDescTable[i].file->writePage(bufPool[i]);
      hashTable->remove(bufDescTable[i].file, bufDescTable[i].pageNo);
      bufDescTable[i].Clear();
    }
  }
}

void BufMgr::allocPage(File* file, PageId& pageNo, Page*& page) {
  FrameId frameNo;
  allocBuf(frameNo);
  bufPool[frameNo] = file->allocatePage();
  pageNo = bufPool[frameNo].page_number();
  hashTable->insert(file, pageNo, frameNo);
  bufDescTable[frameNo].Set(file, pageNo);
  page = &bufPool[frameNo];
}

void BufMgr::disposePage(File* file, const PageId PageNo) {
  FrameId frameNo;
  try {
    hashTable->lookup(file, PageNo, frameNo);
    hashTable->remove(bufDescTable[frameNo].file, bufDescTable[frameNo].pageNo);
    bufDescTable[frameNo].Clear();
    file->deletePage(PageNo);
  } catch (HashNotFoundException e) {
    throw InvalidPageException(PageNo, file->filename());
  }
}

void BufMgr::printSelf(void) {
  BufDesc* tmpbuf;
  int validFrames = 0;

  for (std::uint32_t i = 0; i < numBufs; i++) {
    tmpbuf = &(bufDescTable[i]);
    std::cout << "FrameNo:" << i << " ";
    tmpbuf->Print();

    if (tmpbuf->valid == true) validFrames++;
  }

  std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
}

}  // namespace badgerdb
