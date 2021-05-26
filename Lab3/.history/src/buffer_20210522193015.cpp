/**
 * @author See Contributors.txt for code contributors and overview of BadgerDB.
 *
 * @section LICENSE
 * Copyright (c) 2012 Database Group, Computer Sciences Department, University of Wisconsin-Madison.
 */

#include <memory>
#include <iostream>
#include "buffer.h"
#include "exceptions/buffer_exceeded_exception.h"
#include "exceptions/page_not_pinned_exception.h"
#include "exceptions/page_pinned_exception.h"
#include "exceptions/bad_buffer_exception.h"
#include "exceptions/hash_not_found_exception.h"

namespace badgerdb { 

BufMgr::BufMgr(std::uint32_t bufs)
	: numBufs(bufs) {
	bufDescTable = new BufDesc[bufs];

  for (FrameId i = 0; i < bufs; i++) 
  {
  	bufDescTable[i].frameNo = i;
  	bufDescTable[i].valid = false;
  }

  bufPool = new Page[bufs];

	int htsize = ((((int) (bufs * 1.2))*2)/2)+1;
  hashTable = new BufHashTbl (htsize);  // allocate the buffer hash table

  clockHand = bufs - 1;
}

BufMgr::~BufMgr() {
  for (FrameId i = 0; i < numBufs; i++)
  {
    // if the frame is valid and dirty we need to write back first
    if (bufDescTable[i].valid && bufDescTable[i].dirty)
    {
      flushFile(bufDescTable[i].file);
    }
  }
  delete [] bufDescTable;
  delete [] bufPool;
  delete hashTable;
}

void BufMgr::advanceClock()
{
  clockHand = (clockHand + 1) % numBufs;
}

void BufMgr::allocBuf(FrameId & frame) 
{
  uint32_t pinnedFrameCnt = 0;
  while (true)
  {
    advanceClock();
    if (pinnedFrameCnt == numBufs)
    {
      throw BufferExceededException();
    }

    if (bufDescTable[clockHand].valid == false)
    {
      frame = clockHand;
      bufDescTable[clockHand].Clear();
      break;
    }
    else if (bufDescTable[clockHand].refbit == true)
    {
      bufDescTable[clockHand].refbit = false;
      continue;
    }
    else if (bufDescTable[clockHand].pinCnt > 0)
    {
      pinnedFrameCnt++;
      continue;
    }
    else if (bufDescTable[clockHand].dirty == true)
    {
      bufDescTable[clockHand].file->writePage(bufPool[clockHand]);
      bufStats.diskwrites++;
    }
    frame = clockHand;
    hashTable->remove(bufDescTable[clockHand].file, bufDescTable[clockHand].pageNo);
    bufDescTable[clockHand].Clear();
    break;
  }
}

void BufMgr::readPage(File* file, const PageId pageNo, Page*& page)
{
  try
  {
    FrameId read_frame;
    hashTable->lookup(file, pageNo, read_frame);
    bufDescTable[read_frame].pinCnt++;
    bufDescTable[read_frame].refbit = true;
    page = &bufPool[read_frame];
  }
  catch(HashNotFoundException &)
  {
    FrameId alloc_frame;
    allocBuf(alloc_frame);
    bufPool[alloc_frame] = file->readPage(pageNo);
    bufStats.diskreads++;
    hashTable->insert(file, pageNo, alloc_frame);
    bufDescTable[alloc_frame].Set(file, pageNo);
    page = &bufPool[alloc_frame];
  }
  bufStats.accesses++;
}

void BufMgr::unPinPage(File* file, const PageId pageNo, const bool dirty) 
{
  try
  {
    FrameId frame;
    hashTable->lookup(file, pageNo, frame);
    if (bufDescTable[frame].pinCnt > 0)
    {
      bufDescTable[frame].pinCnt--;
      if (dirty)
      {
        bufDescTable[frame].dirty = dirty;
      }
    }
    else
    {
      throw PageNotPinnedException(file->filename(), pageNo, frame);
    }
  }
  catch(HashNotFoundException &)
  {
  }
}

void BufMgr::flushFile(const File* file) 
{
  for (FrameId i = 0; i < numBufs; i++)
  {
    if (bufDescTable[i].file == file)
    {
      if (bufDescTable[i].pinCnt > 0)
      {
        throw PagePinnedException(file->filename(), bufDescTable[i].pageNo, i);
      }
      if (bufDescTable[i].valid == false)
      {
        throw BadBufferException(i, bufDescTable[i].dirty, bufDescTable[i].valid, bufDescTable[i].refbit);
      }
      if (bufDescTable[i].dirty == true)
      {
        bufDescTable[i].file->writePage(bufPool[i]);
        bufDescTable[i].dirty = false;
        bufStats.diskwrites++;
      }
      hashTable->remove(file, bufDescTable[i].pageNo);
      bufDescTable[i].Clear();
    }
  }
}

void BufMgr::allocPage(File* file, PageId &pageNo, Page*& page) 
{
  Page newPage = file->allocatePage();
  bufStats.diskwrites++;
  pageNo = newPage.page_number();
  FrameId newFrameId;
  allocBuf(newFrameId);
  bufPool[newFrameId] = newPage;
  page = &bufPool[newFrameId];
  hashTable->insert(file, pageNo, newFrameId);
  bufDescTable[newFrameId].Set(file, pageNo);
}

void BufMgr::disposePage(File* file, const PageId PageNo)
{
  try
  {
    FrameId clear_frame;
    hashTable->lookup(file, PageNo, clear_frame);
    bufDescTable[clear_frame].Clear();
    hashTable->remove(file, PageNo);
  }
  catch(HashNotFoundException &)
  {
  }
  // it may throw InvalidPageException, but don't handle it
  file->deletePage(PageNo);
  bufStats.diskwrites++;
}

void BufMgr::printSelf(void) 
{
  BufDesc* tmpbuf;
	int validFrames = 0;
  
  for (std::uint32_t i = 0; i < numBufs; i++)
	{
  	tmpbuf = &(bufDescTable[i]);
		std::cout << "FrameNo:" << i << " ";
		tmpbuf->Print();

  	if (tmpbuf->valid == true)
    	validFrames++;
  }

	std::cout << "Total Number of Valid Frames:" << validFrames << "\n";
}

}
