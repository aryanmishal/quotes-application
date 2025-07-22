import { useState, useEffect } from 'react';
import { Quote } from '@/lib/store/quotes';

// Ensure Quote type includes 'text' property
// Example Quote type definition:
// interface Quote {
//   _id: string;
//   text: string;
//   likes: number;
// }

const [quotes, setQuotes] = useState<Quote[]>([]);

useEffect(() => {
  // Fetch quotes here and set them using setQuotes
  // Example: const fetchedQuotes = await fetchQuotes(); setQuotes(fetchedQuotes);
}, []);

{quotes.map((quote) => (
  <div key={quote._id} className="border p-4 rounded mb-4">
    <div className="flex justify-between items-center">
      <p className="text-gray-700">{quote.text}</p>
      <span className="text-gray-500 text-sm">Likes: {quote.likes}</span>
    </div>
  </div>
))} 