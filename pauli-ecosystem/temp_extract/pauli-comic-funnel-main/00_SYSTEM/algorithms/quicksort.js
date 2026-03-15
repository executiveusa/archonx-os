/**
 * QuickSort Algorithm Implementation
 * Purpose: High-performance sorting for large datasets
 * Time Complexity: O(n log n) average, O(n²) worst case
 * Space Complexity: O(log n) due to recursion stack
 * 
 * Author: PAULI System (Claude Code)
 * Created: 2025-12-21
 * Dependencies: None (pure JavaScript)
 * 
 * Usage:
 *   const arr = [64, 34, 25, 12, 22, 11, 90];
 *   quickSort(arr);
 *   console.log(arr); // [11, 12, 22, 25, 34, 64, 90]
 */

/**
 * Main QuickSort function - Sorts array in-place
 * @param {number[]} arr - Array to sort
 * @param {number} low - Start index (default: 0)
 * @param {number} high - End index (default: arr.length - 1)
 * @returns {void} - Sorts array in-place
 */
function quickSort(arr, low = 0, high = arr.length - 1) {
  if (low < high) {
    // Partition and get pivot index
    const pi = partition(arr, low, high);
    
    // Recursively sort left and right partitions
    quickSort(arr, low, pi - 1);
    quickSort(arr, pi + 1, high);
  }
}

/**
 * Partition function - Rearranges array around pivot
 * @param {number[]} arr - Array to partition
 * @param {number} low - Start index
 * @param {number} high - End index
 * @returns {number} - Pivot index after partitioning
 */
function partition(arr, low, high) {
  // Choose last element as pivot
  const pivot = arr[high];
  
  // Index of smaller element - indicates the right position
  // of pivot found so far
  let i = low - 1;
  
  // Traverse through all elements
  // Compare each element with pivot
  for (let j = low; j < high; j++) {
    if (arr[j] < pivot) {
      i++;
      // Swap arr[i] and arr[j]
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }
  
  // Swap arr[i+1] and arr[high] (pivot)
  [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
  
  return i + 1;
}

/**
 * Optimized QuickSort with Random Pivot
 * Reduces probability of O(n²) worst case
 * @param {number[]} arr - Array to sort
 * @param {number} low - Start index
 * @param {number} high - End index
 */
function quickSortRandomPivot(arr, low = 0, high = arr.length - 1) {
  if (low < high) {
    const pi = partitionRandom(arr, low, high);
    quickSortRandomPivot(arr, low, pi - 1);
    quickSortRandomPivot(arr, pi + 1, high);
  }
}

/**
 * Partition with random pivot selection
 * @param {number[]} arr - Array to partition
 * @param {number} low - Start index
 * @param {number} high - End index
 * @returns {number} - Pivot index
 */
function partitionRandom(arr, low, high) {
  // Random index between low and high
  const randomIndex = Math.floor(Math.random() * (high - low + 1)) + low;
  
  // Swap random element with last element
  [arr[randomIndex], arr[high]] = [arr[high], arr[randomIndex]];
  
  // Use standard partition
  return partition(arr, low, high);
}

/**
 * Three-Way Partition (Bentley-McIlroy)
 * Optimized for arrays with duplicate elements
 * @param {number[]} arr - Array to sort
 * @param {number} low - Start index
 * @param {number} high - End index
 */
function quickSortThreeWay(arr, low = 0, high = arr.length - 1) {
  if (low < high) {
    const [lt, gt] = partitionThreeWay(arr, low, high);
    quickSortThreeWay(arr, low, lt - 1);
    quickSortThreeWay(arr, gt + 1, high);
  }
}

/**
 * Three-way partition (handles duplicates efficiently)
 * Returns [lt, gt] where:
 * - arr[low..lt-1] < pivot
 * - arr[lt..gt] == pivot
 * - arr[gt+1..high] > pivot
 * @returns {[number, number]} - [lt, gt] indices
 */
function partitionThreeWay(arr, low, high) {
  const pivot = arr[low];
  let lt = low;
  let gt = high;
  let i = low + 1;
  
  while (i <= gt) {
    if (arr[i] < pivot) {
      [arr[lt], arr[i]] = [arr[i], arr[lt]];
      lt++;
      i++;
    } else if (arr[i] > pivot) {
      [arr[i], arr[gt]] = [arr[gt], arr[i]];
      gt--;
    } else {
      i++;
    }
  }
  
  return [lt, gt];
}

/**
 * Functional QuickSort (immutable)
 * Returns new sorted array without modifying original
 * @param {number[]} arr - Array to sort
 * @returns {number[]} - New sorted array
 */
function quickSortFunctional(arr) {
  if (arr.length <= 1) return arr;
  
  const [pivot, ...rest] = arr;
  const left = rest.filter(x => x < pivot);
  const right = rest.filter(x => x >= pivot);
  
  return [...quickSortFunctional(left), pivot, ...quickSortFunctional(right)];
}

/**
 * QuickSort with Custom Comparator
 * Allows sorting by custom comparison logic
 * @param {any[]} arr - Array to sort
 * @param {Function} comparator - Function returning -1, 0, or 1
 * @param {number} low - Start index
 * @param {number} high - End index
 */
function quickSortCustom(arr, comparator, low = 0, high = arr.length - 1) {
  if (low < high) {
    const pi = partitionCustom(arr, comparator, low, high);
    quickSortCustom(arr, comparator, low, pi - 1);
    quickSortCustom(arr, comparator, pi + 1, high);
  }
}

/**
 * Partition with custom comparator
 */
function partitionCustom(arr, comparator, low, high) {
  const pivot = arr[high];
  let i = low - 1;
  
  for (let j = low; j < high; j++) {
    if (comparator(arr[j], pivot) < 0) {
      i++;
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }
  
  [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
  return i + 1;
}

// ============================================================================
// PERFORMANCE TESTING & BENCHMARKING
// ============================================================================

/**
 * Benchmark function performance
 * @param {Function} fn - Function to benchmark
 * @param {any[]} args - Arguments to pass to function
 * @param {number} iterations - Number of iterations
 */
function benchmark(fn, args, iterations = 1000) {
  const start = performance.now();
  
  for (let i = 0; i < iterations; i++) {
    fn(...args);
  }
  
  const end = performance.now();
  return {
    totalTime: end - start,
    averageTime: (end - start) / iterations,
    iterations
  };
}

/**
 * Generate test array of given size
 * @param {number} size - Array size
 * @param {string} type - 'random' | 'sorted' | 'reverse' | 'nearly-sorted'
 */
function generateTestArray(size, type = 'random') {
  const arr = Array.from({ length: size }, () => Math.floor(Math.random() * 1000));
  
  if (type === 'sorted') return arr.sort((a, b) => a - b);
  if (type === 'reverse') return arr.sort((a, b) => b - a);
  if (type === 'nearly-sorted') {
    const sorted = arr.sort((a, b) => a - b);
    // Shuffle 5% of elements
    for (let i = 0; i < Math.floor(size * 0.05); i++) {
      const idx1 = Math.floor(Math.random() * size);
      const idx2 = Math.floor(Math.random() * size);
      [sorted[idx1], sorted[idx2]] = [sorted[idx2], sorted[idx1]];
    }
    return sorted;
  }
  
  return arr;
}

// ============================================================================
// EXPORTS (For Node.js/Module Usage)
// ============================================================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    quickSort,
    quickSortRandomPivot,
    quickSortThreeWay,
    quickSortFunctional,
    quickSortCustom,
    partition,
    partitionRandom,
    partitionThreeWay,
    partitionCustom,
    benchmark,
    generateTestArray
  };
}

// ============================================================================
// EXAMPLE USAGE & TEST CASES
// ============================================================================

/*
// Basic usage
const arr1 = [64, 34, 25, 12, 22, 11, 90];
quickSort(arr1);
console.log('Basic sort:', arr1); // [11, 12, 22, 25, 34, 64, 90]

// Random pivot (better for real-world data)
const arr2 = [64, 34, 25, 12, 22, 11, 90];
quickSortRandomPivot(arr2);
console.log('Random pivot:', arr2); // [11, 12, 22, 25, 34, 64, 90]

// Three-way partition (good for duplicates)
const arr3 = [5, 2, 8, 2, 9, 2, 1, 5];
quickSortThreeWay(arr3);
console.log('Three-way:', arr3); // [1, 2, 2, 2, 5, 5, 8, 9]

// Functional (immutable)
const arr4 = [64, 34, 25, 12, 22, 11, 90];
const sorted = quickSortFunctional(arr4);
console.log('Functional:', sorted); // [11, 12, 22, 25, 34, 64, 90]
console.log('Original:', arr4); // [64, 34, 25, 12, 22, 11, 90] - unchanged

// Custom comparator (objects)
const people = [
  { name: 'Alice', age: 30 },
  { name: 'Bob', age: 25 },
  { name: 'Charlie', age: 35 }
];

quickSortCustom(people, 
  (a, b) => a.age < b.age ? -1 : (a.age > b.age ? 1 : 0)
);
// Sort by age in ascending order

// Benchmarking
const testArr = generateTestArray(10000, 'random');
const result = benchmark(() => quickSort(testArr.slice()), [], 100);
console.log(`Sorted 10,000 items in ${result.averageTime.toFixed(2)}ms average`);
*/
