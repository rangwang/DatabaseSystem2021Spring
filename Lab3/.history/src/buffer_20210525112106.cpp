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

void BufMgr::allocBuf(FrameId& frame) {}

void BufMgr::readPage(File* file, const PageId pageNo, Page*& page) {
  FrameId frameNo;
  try {
    hashTable->lookup(file, pageNo, frameNo);
    bufDescTable[frameNo].pinCnt++;
    bufDescTable[frameNo].refbit = true;
  } catch (HashNotFoundException e) {
    allocBuf(frameNo);
    bufPool[frameNo] = file->readPage(pageNo);
    hashTable->insert(file, pageNo, frameNo);
    bufDescTable[frameNo].Set(file, pageNo);
  }
  page = &bufPool[frameNo];
}

void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) {
  try {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);
    if (bufDescTable[frame].pinCnt > 0) {
      bufDescTable[frame].pinCnt--;
      if (dirty) {
        bufDescTable[frame].dirty = dirty;
      }
    } else {
      throw PageNotPinnedException(file->filename(), pageNo, frame);
    }
  } catch (HashNotFoundException&) {
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
  hashTable->lookup(file, PageNo, frameNo);
  hashTable->remove(file, PageNo);
  bufDescTable[frameNo].Clear();
  file->deletePage(PageNo);
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
