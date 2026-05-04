# VU Performance Oriented Computing -- Sheet 08

Author: Marco Fröhlich

# Exercise A -- False Sharing

The pull request aims to solve a false sharing problem. Before the merge conflict padding was used to ensure that instances of the different elements of the `thread` property of the class `ObjectUseData` end up in different cache lines. This is necessary so that each thread can work on this variable and not invalidate the cache line for all other threads once a change happens.
The same thing was done for the struct `AlignedSharedMutex`, each of the locks ends up in a different cache line.

With the new implementation the developers make use of the `get_hardware_destructive_interference_size()` function that was introduced with `C++ 17`. A call of this function returns the "[m]inimum offset between two objects to avoid false sharing." Additionally, the specifier `alignas()` that tells the compiler about specific alignment requirements of a variable, struct, etc. was used. Together this ensures that the objects annotated with this end up in different cache lines. 

If the function `get_hardware_destructive_interference_size()` is not supported by the system, a default value of 64 bytes is returned. According to research this is a common value for most systems, but not all. As the comment already suggests the Apple M1 has a cache line size of 128 bytes, so in that case the issue would not be resolved.

The usage of this will solve the false sharing problem, but also introduces a memory overhead, especially when many instances of the mentioned classes are created.


# Exercise B -- Data Structure Selection

*Disclaimer:* I used Mistral's *Le Chat* to search for GitHub repositories to find ones match the criteria for this exercise. As a prompt I simply used the first sentence of the task description.

I used the following pull request of the [jersey project](https://github.com/eclipse-ee4j/jersey/pull/4300) for my analysis, I never have worked with this framework before nor have even heard of it. But according to the 726 stars and 377 forks (as of 04.05.2026) and the regular commits and releases this project is actively maintained and used by people.

In this pull request a couple of changes to data-structures were implemented, but the one I will focus on is in line 206/209:
```java
- this.childResource = new ArrayList<>();
+ this.childResource = new LinkedList<>();
```
The reasoning given in the commit message was that they wanted to keep the fast `Iterator.remove()` functionality. Linked lists over better performance for frequent insertions and deletions in the middle of the list. This is because removing an element only requires moving one link form the previous element to refer to the next element in line, whereas with an Array List all elements succeeding the removed one need to moved to fill the gap. So in terms access behavior the complexity this optimization improves the complexity from $O(n)$ to $O(1)$, which can be a significant improvement in terms of performance.


If this change is looked from a view point of caching and memory hierarchy the *Array List* would have been the better choice since its elements lay sequentially in memory which is very cache friendly. Whereas in a *Linked List* the elements are scattered in memory and the CPU has to perform pointer chasing during traversal, which is not optimal in terms of cache usage.

But in terms of data type it seems to be important that the collection does not contain duplicates, which neither of the List types support. Since merging if different Resources is the intended use case of this application, it would make more sense to me to have a data structure that requires this at the beginning and not convert the two merging partners to Sets and to invoke this property. The runtime complexity of the `add()`, `remove()` and `contains()` methods would not change with this adaptation. But a *Set* would not have the order property, which might be the more important property for the implementation.

By looking at the implementation I can not make any statement about the amount of data that might be managed with the data structure during runtime. But is seams like this is heavily usage dependent.