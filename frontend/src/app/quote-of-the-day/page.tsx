'use client'

import { useEffect, useState } from 'react'
import { useQuotesStore } from '@/lib/store/quotes'
import { quotesAPI } from '@/lib/api'
import { toast } from 'sonner'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function QuoteOfTheDayPage() {
  const { quotes, setQuotes, loading, setLoading } = useQuotesStore()
  const [randomQuote, setRandomQuote] = useState<any>(null)

  useEffect(() => {
    fetchQuotes()
  }, [])

  const fetchQuotes = async () => {
    setLoading(true)
    try {
      const data = await quotesAPI.getQuotes()
      setQuotes(data)
      // Select a random quote
      const randomIndex = Math.floor(Math.random() * data.length)
      setRandomQuote(data[randomIndex])
    } catch (err) {
      console.error('Fetch quotes error:', err)
      toast.error('Failed to fetch quotes')
    } finally {
      setLoading(false)
    }
  }

  const handleNewQuote = () => {
    const randomIndex = Math.floor(Math.random() * quotes.length)
    setRandomQuote(quotes[randomIndex])
  }

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardContent className="pt-6">
          {randomQuote ? (
            <div className="text-center space-y-6">
              <p className="text-2xl font-medium italic">"{randomQuote.quote}"</p>
              <p className="text-lg text-gray-600">- {randomQuote.author}</p>
              <Button onClick={handleNewQuote} variant="outline">
                Get Another Quote
              </Button>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              No quotes available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 