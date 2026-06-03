#include "unrolled_linked_list.hpp"

#include <cstring>

template <size_t StorageSize>
UnrolledLinkedList<StorageSize>::UnrolledLinkedList() : head(nullptr), elementCount(0) {}

template <size_t StorageSize>
UnrolledLinkedList<StorageSize>::~UnrolledLinkedList() {
	Node* current = head;
	while(current != nullptr) {
		Node* next = current->next;
		delete current;
		current = next;
	}
}

template <size_t StorageSize>
size_t UnrolledLinkedList<StorageSize>::size() const {
	return elementCount;
}

template <size_t StorageSize>
typename UnrolledLinkedList<StorageSize>::Node* UnrolledLinkedList<StorageSize>::findNode(size_t index, size_t& localIndex) {
	if(head == nullptr) {
		localIndex = 0;
		return nullptr;
	}

	Node* current = head;
	size_t currentIndex = 0;

	while(current != nullptr) {
		if(index < currentIndex + static_cast<size_t>(current->numElements)) {
			localIndex = index - currentIndex;
			return current;
		}

		currentIndex += static_cast<size_t>(current->numElements);
		if(current->next == nullptr) {
			localIndex = static_cast<size_t>(current->numElements);
			return current;
		}
		current = current->next;
	}

	localIndex = 0;
	return nullptr;
}

template <size_t StorageSize>
void UnrolledLinkedList<StorageSize>::splitNode(Node* node) {
	if(node == nullptr || node->numElements < nodeCapacity) {
		return;
	}

	Node* newNode = new Node();
	int moveCount = node->numElements / 2;
	int start = node->numElements - moveCount;
	std::memcpy(newNode->data, node->data + start * StorageSize, moveCount * StorageSize);
	newNode->numElements = moveCount;
	node->numElements = start;

	newNode->next = node->next;
	node->next = newNode;
}

template <size_t StorageSize>
void* UnrolledLinkedList<StorageSize>::insert(size_t index, void* value) {
	if(head == nullptr) {
		head = new Node();
		std::memcpy(head->data, value, StorageSize);
		head->numElements = 1;
		head->next = nullptr;
		elementCount = 1;
		return head->data;
	}

	if(index > elementCount) {
		index = elementCount;
	}

	Node* current = head;
	size_t currentIndex = 0;

	while(current != nullptr && index > currentIndex + static_cast<size_t>(current->numElements)) {
		currentIndex += static_cast<size_t>(current->numElements);
		current = current->next;
	}

	if(current == nullptr) {
		current = head;
		currentIndex = 0;
		while(current->next != nullptr) {
			currentIndex += static_cast<size_t>(current->numElements);
			current = current->next;
		}
		index = currentIndex + static_cast<size_t>(current->numElements);
	}

	if(current->numElements == nodeCapacity) {
		splitNode(current);
		if(index > currentIndex + static_cast<size_t>(current->numElements)) {
			currentIndex += static_cast<size_t>(current->numElements);
			current = current->next;
		}
	}

	size_t localIndex = index - currentIndex;
	// shift bytes to make room
	for(int i = static_cast<int>(current->numElements); i > static_cast<int>(localIndex); --i) {
		std::memcpy(current->data + i * StorageSize, current->data + (i - 1) * StorageSize, StorageSize);
	}
	std::memcpy(current->data + localIndex * StorageSize, value, StorageSize);
	current->numElements++;
	elementCount++;
	return current->data + localIndex * StorageSize;
}

template <size_t StorageSize>
void UnrolledLinkedList<StorageSize>::remove(size_t index) {
	if(head == nullptr || index >= elementCount) {
		return;
	}

	Node* current = head;
	Node* previous = nullptr;
	size_t currentIndex = 0;

	while(current != nullptr && index >= currentIndex + static_cast<size_t>(current->numElements)) {
		currentIndex += static_cast<size_t>(current->numElements);
		previous = current;
		current = current->next;
	}

	if(current == nullptr) {
		return;
	}

	size_t localIndex = index - currentIndex;
	for(size_t i = localIndex; i + 1 < static_cast<size_t>(current->numElements); ++i) {
		std::memcpy(current->data + i * StorageSize, current->data + (i + 1) * StorageSize, StorageSize);
	}
	current->numElements--;
	elementCount--;

	if(current->numElements == 0) {
		if(previous == nullptr) {
			head = current->next;
		} else {
			previous->next = current->next;
		}
		delete current;
		return;
	}

	if(current->next != nullptr && current->numElements + current->next->numElements <= nodeCapacity) {
		Node* next = current->next;
		std::memcpy(current->data + current->numElements * StorageSize, next->data, next->numElements * StorageSize);
		current->numElements += next->numElements;
		current->next = next->next;
		delete next;
	}
}

template <size_t StorageSize>
void* UnrolledLinkedList<StorageSize>::read(size_t index) {
	if(head == nullptr || index >= elementCount) {
		return nullptr;
	}

	Node* current = head;
	size_t currentIndex = 0;
	while(current != nullptr && index >= currentIndex + static_cast<size_t>(current->numElements)) {
		currentIndex += static_cast<size_t>(current->numElements);
		current = current->next;
	}

	if(current == nullptr) {
		return nullptr;
	}

	return current->data + (index - currentIndex) * StorageSize;
}

template <size_t StorageSize>
void UnrolledLinkedList<StorageSize>::write(size_t index, void* value) {
	if(head == nullptr || index >= elementCount) {
		return;
	}

	Node* current = head;
	size_t currentIndex = 0;
	while(current != nullptr && index >= currentIndex + static_cast<size_t>(current->numElements)) {
		currentIndex += static_cast<size_t>(current->numElements);
		current = current->next;
	}

	if(current == nullptr) {
		return;
	}

	std::memcpy(current->data + (index - currentIndex) * StorageSize, value, StorageSize);
}

// explicit instantiations
template class UnrolledLinkedList<8>;
template class UnrolledLinkedList<512>;
template class UnrolledLinkedList<8000000>;