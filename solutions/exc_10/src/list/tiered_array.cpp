#include "tiered_array.hpp"

#include <cstring>
#include <utility>

template <size_t StorageSize> TieredArray<StorageSize>::TieredArray() : blocks(), elementCount(0) {}

template <size_t StorageSize> TieredArray<StorageSize>::~TieredArray() = default;

template <size_t StorageSize> void* TieredArray<StorageSize>::insert(size_t index, void* value) {
	if(index >= elementCount) {
		index = elementCount;
	}

	if(value == nullptr) {
		return nullptr;
	}

	if(blocks.empty()) {
		blocks.emplace_back();
	}

	BlockPosition position = locate(index);
	if(position.blockIndex == blocks.size()) {
		blocks.emplace_back();
		position.blockIndex = blocks.size() - 1;
		position.offset = blocks.back().size() / StorageSize;
	}

	std::vector<char>& block = blocks[position.blockIndex];
	size_t insertBytePos = position.offset * StorageSize;
	char* bytes = static_cast<char*>(value);
	block.insert(block.begin() + static_cast<std::ptrdiff_t>(insertBytePos), bytes,
	             bytes + StorageSize);
	++elementCount;

	size_t elemCount = block.size() / StorageSize;
	if(elemCount > blockCapacity) {
		splitBlock(position.blockIndex);
	}

	return block.data() + insertBytePos;
}

template <size_t StorageSize> void TieredArray<StorageSize>::remove(size_t index) {
	if(index >= elementCount || blocks.empty()) {
		return;
	}

	BlockPosition position = locate(index);
	if(position.blockIndex >= blocks.size()) {
		return;
	}

	std::vector<char>& block = blocks[position.blockIndex];
	size_t elemCount = block.size() / StorageSize;
	if(position.offset >= elemCount) {
		return;
	}

	size_t eraseStart = position.offset * StorageSize;
	block.erase(block.begin() + static_cast<std::ptrdiff_t>(eraseStart),
	            block.begin() + static_cast<std::ptrdiff_t>(eraseStart + StorageSize));
	--elementCount;

	if(block.empty()) {
		blocks.erase(blocks.begin() + static_cast<std::ptrdiff_t>(position.blockIndex));
		return;
	}

	if(position.blockIndex + 1 < blocks.size()) {
		std::vector<char>& nextBlock = blocks[position.blockIndex + 1];
		size_t nextElemCount = nextBlock.size() / StorageSize;
		if(elemCount + nextElemCount <= blockCapacity) {
			block.insert(block.end(), nextBlock.begin(), nextBlock.end());
			blocks.erase(blocks.begin() + static_cast<std::ptrdiff_t>(position.blockIndex + 1));
		}
	}
}

template <size_t StorageSize> void* TieredArray<StorageSize>::read(size_t index) {
	if(index >= elementCount || blocks.empty()) {
		return nullptr;
	}

	BlockPosition position = locate(index);
	if(position.blockIndex >= blocks.size()) {
		return nullptr;
	}

	std::vector<char>& block = blocks[position.blockIndex];
	size_t elemCount = block.size() / StorageSize;
	if(position.offset >= elemCount) {
		return nullptr;
	}

	return static_cast<void*>(block.data() + position.offset * StorageSize);
}

template <size_t StorageSize> void TieredArray<StorageSize>::write(size_t index, void* value) {
	if(index >= elementCount || blocks.empty() || value == nullptr) {
		return;
	}

	BlockPosition position = locate(index);
	if(position.blockIndex >= blocks.size()) {
		return;
	}

	std::vector<char>& block = blocks[position.blockIndex];
	size_t elemCount = block.size() / StorageSize;
	if(position.offset >= elemCount) {
		return;
	}

	std::memcpy(block.data() + position.offset * StorageSize, value, StorageSize);
}

template <size_t StorageSize> size_t TieredArray<StorageSize>::size() const {
	return elementCount;
}

template <size_t StorageSize>
typename TieredArray<StorageSize>::BlockPosition
TieredArray<StorageSize>::locate(size_t index) const {
	if(index >= elementCount) {
		return { blocks.size(), 0 };
	}

	BlockPosition position{ blocks.size(), 0 };
	size_t baseIndex = 0;

	for(size_t blockIndex = 0; blockIndex < blocks.size(); ++blockIndex) {
		const std::vector<char>& block = blocks[blockIndex];
		size_t elemCount = block.size() / StorageSize;
		if(index < baseIndex + elemCount) {
			position.blockIndex = blockIndex;
			position.offset = index - baseIndex;
			return position;
		}
		baseIndex += elemCount;
	}

	if(!blocks.empty()) {
		position.blockIndex = blocks.size() - 1;
		position.offset = blocks.back().size() / StorageSize;
	}

	return position;
}

template <size_t StorageSize> void TieredArray<StorageSize>::splitBlock(size_t blockIndex) {
	if(blockIndex >= blocks.size()) {
		return;
	}

	std::vector<char>& block = blocks[blockIndex];
	size_t elemCount = block.size() / StorageSize;
	if(elemCount <= blockCapacity) {
		return;
	}

	size_t moveCount = elemCount / 2;
	size_t startElem = elemCount - moveCount;
	size_t startByte = startElem * StorageSize;
	std::vector<char> newBlock;
	newBlock.reserve(startByte);
	newBlock.insert(newBlock.end(), block.begin() + static_cast<std::ptrdiff_t>(startByte),
	                block.end());
	block.erase(block.begin() + static_cast<std::ptrdiff_t>(startByte), block.end());
	blocks.insert(blocks.begin() + static_cast<std::ptrdiff_t>(blockIndex + 1),
	              std::move(newBlock));
}

// explicit instantiations
template class TieredArray<8>;
template class TieredArray<512>;
template class TieredArray<8000000>;