import { create } from 'zustand'

export interface Quote {
  _id: string
  quote?: string
  text?: string
  author: string
  tags?: string
  likes: number
  dislikes?: number
  is_active?: boolean
  user_id?: string
  user_name?: string
  created_at?: string
  updated_at?: string
  is_liked?: boolean
  is_disliked?: boolean
}

interface QuotesState {
  quotes: Quote[]
  loading: boolean
  error: string | null
  setQuotes: (quotes: Quote[]) => void
  addQuote: (quote: Quote) => void
  updateQuote: (id: string, quote: Partial<Quote>) => void
  deleteQuote: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useQuotesStore = create<QuotesState>((set) => ({
  quotes: [],
  loading: false,
  error: null,
  setQuotes: (quotes) => set({ quotes }),
  addQuote: (quote) => set((state) => ({ quotes: [...state.quotes, quote] })),
  updateQuote: (id, updatedQuote) =>
    set((state) => ({
      quotes: state.quotes.map((quote) =>
        quote._id === id ? { ...quote, ...updatedQuote } : quote
      ),
    })),
  deleteQuote: (id) =>
    set((state) => ({
      quotes: state.quotes.filter((quote) => quote._id !== id),
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
})) 