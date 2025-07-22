'use client'

import { useEffect, useState } from 'react'
import { useQuotesStore } from '@/lib/store/quotes'
import { quotesAPI } from '@/lib/api'
import { useAuthStore } from '@/lib/store/auth'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

export default function QuotesPage() {
  const { quotes, setQuotes, loading, setLoading, error, setError } = useQuotesStore()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const [newQuote, setNewQuote] = useState({ text: '', author: '' })

  useEffect(() => {
    fetchQuotes()
  }, [])

  const fetchQuotes = async () => {
    setLoading(true)
    try {
      const data = await quotesAPI.getQuotes()
      setQuotes(data)
    } catch (err) {
      toast.error('Failed to fetch quotes')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateQuote = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!isAuthenticated) return

    try {
      await quotesAPI.createQuote({
        ...newQuote,
        likes: 0,
        dislikes: 0
      })
      setNewQuote({ text: '', author: '' })
      toast.success('Quote created successfully!')
      fetchQuotes()
    } catch (err) {
      toast.error('Failed to create quote')
    }
  }

  const handleDeleteQuote = async (id: string) => {
    if (!isAuthenticated) return

    try {
      await quotesAPI.deleteQuote(id)
      toast.success('Quote deleted successfully!')
      fetchQuotes()
    } catch (err) {
      toast.error('Failed to delete quote')
    }
  }

  const handleLikeQuote = async (id: string) => {
    try {
      await quotesAPI.likeQuote(id)
      fetchQuotes()
    } catch (err) {
      toast.error('Failed to like quote')
    }
  }

  const handleDislikeQuote = async (id: string) => {
    try {
      await quotesAPI.dislikeQuote(id)
      fetchQuotes()
    } catch (err) {
      toast.error('Failed to dislike quote')
    }
  }

  if (loading) return <div className="flex justify-center items-center min-h-screen">Loading...</div>
  if (error) return <div className="text-red-500 text-center">{error}</div>

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Quotes</h1>

      {isAuthenticated && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Add New Quote</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateQuote} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="quote">Quote</Label>
                <Textarea
                  id="quote"
                  value={newQuote.text}
                  onChange={(e) => setNewQuote({ ...newQuote, text: e.target.value })}
                  placeholder="Enter your quote"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="author">Author</Label>
                <Input
                  id="author"
                  type="text"
                  value={newQuote.author}
                  onChange={(e) => setNewQuote({ ...newQuote, author: e.target.value })}
                  placeholder="Enter author name"
                  required
                />
              </div>
              <Button type="submit">Add Quote</Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {quotes.map((quote) => (
          <Card key={quote.id}>
            <CardContent className="pt-6">
              <p className="text-lg mb-2">{quote.text}</p>
              <p className="text-sm text-gray-600 mb-4">- {quote.author}</p>
              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleLikeQuote(quote.id)}
                  className="text-gray-500 hover:text-green-500"
                >
                  👍 {quote.likes}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDislikeQuote(quote.id)}
                  className="text-gray-500 hover:text-red-500"
                >
                  👎 {quote.dislikes}
                </Button>
                {isAuthenticated && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteQuote(quote.id)}
                  >
                    Delete
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
} 