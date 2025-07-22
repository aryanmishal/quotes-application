'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuotesStore } from '@/lib/store/quotes'
import { useAuthStore } from '@/lib/store/auth'
import { quotesAPI } from '@/lib/api'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { X, User, ChevronUp } from 'lucide-react'
import { Quote } from '@/lib/store/quotes'
import { ThemeToggle } from '@/components/theme-toggle'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const ITEMS_PER_PAGE = 30
const MAX_QUOTE_LENGTH = 300

export default function HomePage() {
  const { quotes, setQuotes, loading, setLoading } = useQuotesStore()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)
  const [newQuote, setNewQuote] = useState({ quote: '', author: '', tags: '' })
  const [authors, setAuthors] = useState<string[]>([])
  const [editingQuote, setEditingQuote] = useState<Quote | null>(null)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [quoteToDelete, setQuoteToDelete] = useState<string | null>(null)
  const [quoteSearch, setQuoteSearch] = useState('')
  const [authorSearch, setAuthorSearch] = useState('')
  const [activeTab, setActiveTab] = useState('home')
  const [randomQuote, setRandomQuote] = useState<Quote | null>(null)
  const [quotesPage, setQuotesPage] = useState(1)
  const [authorsPage, setAuthorsPage] = useState(1)
  const [searchFilter, setSearchFilter] = useState('all')
  const [isReactionsDialogOpen, setIsReactionsDialogOpen] = useState(false)
  const [selectedQuoteId, setSelectedQuoteId] = useState<string | null>(null)
  const [reactions, setReactions] = useState<{ likes: string[], dislikes: string[] }>({ likes: [], dislikes: [] })
  const [reactionsLoading, setReactionsLoading] = useState(false)
  const [isNewQuoteDialogOpen, setIsNewQuoteDialogOpen] = useState(false)
  const [quoteCharCount, setQuoteCharCount] = useState(0)
  const [myQuotesSubTab, setMyQuotesSubTab] = useState('my')
  const router = useRouter()

  // Hydrate auth store on page load
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    // Try to get auth state from persistent storage first
    const persistentState = localStorage.getItem('auth-storage')
    if (persistentState) {
      try {
        const { state } = JSON.parse(persistentState)
        if (state.rememberMe && state.isAuthenticated) {
          useAuthStore.setState(state)
          return
        }
      } catch (error) {
        console.error('Error parsing persistent auth state:', error)
      }
    }

    // If no persistent state or rememberMe is false, try session storage
    const sessionState = sessionStorage.getItem('auth-storage')
    if (sessionState) {
      try {
        const { state } = JSON.parse(sessionState)
        if (state.isAuthenticated) {
          useAuthStore.setState(state)
        }
      } catch (error) {
        console.error('Error parsing session auth state:', error)
      }
    }
  }, [])

  // Helper to get today's date string
  const getTodayString = () => {
    return new Date().toISOString().split('T')[0]
  }

  // Helper to get a random quote from a list, avoiding recent ones
  const getRandomQuoteFromList = (quotes: Quote[], recentQuotes: string[]) => {
    const availableQuotes = quotes.filter(quote => !recentQuotes.includes(quote._id))
    if (availableQuotes.length === 0) {
      // If all quotes have been shown, allow repeats
      return quotes[Math.floor(Math.random() * quotes.length)]
    }
    return availableQuotes[Math.floor(Math.random() * availableQuotes.length)]
  }

  useEffect(() => {
    fetchQuotes()
    // Handle tab parameter from URL in client-side only
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const tabParam = params.get('tab')
      if (tabParam && ['home', 'quotes', 'authors', 'manage'].includes(tabParam)) {
        setActiveTab(tabParam)
      }
    }
  }, [])

  // Set quote of the day based on new logic
  useEffect(() => {
    if (!quotes || quotes.length === 0) return;
    if (typeof window === 'undefined') return;

    const today = getTodayString();
    const storedQuoteData = localStorage.getItem('quoteOfTheDayV2');
    let recentQuotes: string[] = [];
    let lastDate = '';
    if (storedQuoteData) {
      try {
        const { date, recentQuotes: storedRecent } = JSON.parse(storedQuoteData);
        lastDate = date;
        if (Array.isArray(storedRecent)) recentQuotes = storedRecent;
      } catch {}
    }

    // Only keep last 2 days' quote IDs
    if (recentQuotes.length > 2) recentQuotes = recentQuotes.slice(0, 2);

    let candidateQuotes: Quote[] = [];
    let chosenQuote: Quote | null = null;
    if (isAuthenticated && user) {
      // 1. Try liked quotes
      candidateQuotes = quotes.filter(q => q.is_liked);
      if (candidateQuotes.length > 0) {
        chosenQuote = getRandomQuoteFromList(candidateQuotes, recentQuotes);
      } else {
        // 2. Try user's own quotes
        candidateQuotes = quotes.filter(q => q.user_id === user.id);
        if (candidateQuotes.length > 0) {
          chosenQuote = getRandomQuoteFromList(candidateQuotes, recentQuotes);
        }
      }
    }
    // 3. Fallback: any random quote
    if (!chosenQuote) {
      chosenQuote = getRandomQuoteFromList(quotes, recentQuotes);
    }

    // If it's a new day or quote not set, update
    if (!storedQuoteData || lastDate !== today) {
      // Add new quote to the front of recentQuotes
      const newRecentQuotes = [chosenQuote._id, ...recentQuotes].slice(0, 2);
      localStorage.setItem('quoteOfTheDayV2', JSON.stringify({
        quote: chosenQuote,
        date: today,
        recentQuotes: newRecentQuotes
      }));
      setRandomQuote(chosenQuote);
    } else {
      // Use the stored quote for today
      try {
        const { quote } = JSON.parse(storedQuoteData);
        setRandomQuote(quote);
      } catch {
        setRandomQuote(chosenQuote);
      }
    }
  }, [quotes, isAuthenticated, user]);

  // Update URL when tab changes - client-side only
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href)
      url.searchParams.set('tab', activeTab)
      window.history.replaceState({}, '', url)
    }
  }, [activeTab])

  const fetchQuotes = async () => {
    setLoading(true)
    try {
      const data = await quotesAPI.getQuotes()
      setQuotes(data)
      
      if (typeof window !== 'undefined') {
        // Get stored quote data - client-side only
        const storedQuoteData = localStorage.getItem('quoteOfTheDay')
        const today = getTodayString()
        
        if (storedQuoteData) {
          const { quote, date, recentQuotes } = JSON.parse(storedQuoteData)
          
          // If it's a new day, get a new quote
          if (date !== today) {
            const newQuote = getRandomQuoteFromList(data, recentQuotes)
            const newRecentQuotes = [newQuote._id, ...recentQuotes.slice(0, 9)] // Keep last 10 quotes
            
            localStorage.setItem('quoteOfTheDay', JSON.stringify({
              quote: newQuote,
              date: today,
              recentQuotes: newRecentQuotes
            }))
            
            setRandomQuote(newQuote)
          } else {
            // Use the stored quote for today
            setRandomQuote(quote)
          }
        } else {
          // First time visit, get a random quote
          const newQuote = data[Math.floor(Math.random() * data.length)]
          localStorage.setItem('quoteOfTheDay', JSON.stringify({
            quote: newQuote,
            date: today,
            recentQuotes: [newQuote._id]
          }))
          setRandomQuote(newQuote)
        }
      } else {
        // Server-side rendering - just set a random quote without storage
        const newQuote = data[Math.floor(Math.random() * data.length)]
        setRandomQuote(newQuote)
      }

      // Extract unique authors
      const authorSet = new Set<string>()
      data.forEach((quote: Quote) => authorSet.add(quote.author))
      setAuthors(Array.from(authorSet))
    } catch (err) {
      console.error('Fetch quotes error:', err)
      toast.error('Failed to fetch quotes')
    } finally {
      setLoading(false)
    }
  }

  const handleNewRandomQuote = () => {
    if (!quotes || quotes.length === 0 || typeof window === 'undefined') return;
    const today = getTodayString();
    const storedQuoteData = localStorage.getItem('quoteOfTheDayV2');
    let recentQuotes: string[] = [];
    if (storedQuoteData) {
      try {
        const { recentQuotes: storedRecent } = JSON.parse(storedQuoteData);
        if (Array.isArray(storedRecent)) recentQuotes = storedRecent;
      } catch {}
    }
    if (recentQuotes.length > 2) recentQuotes = recentQuotes.slice(0, 2);

    let candidateQuotes: Quote[] = [];
    let chosenQuote: Quote | null = null;
    if (isAuthenticated && user) {
      candidateQuotes = quotes.filter(q => q.is_liked);
      if (candidateQuotes.length > 0) {
        chosenQuote = getRandomQuoteFromList(candidateQuotes, recentQuotes);
      } else {
        candidateQuotes = quotes.filter(q => q.user_id === user.id);
        if (candidateQuotes.length > 0) {
          chosenQuote = getRandomQuoteFromList(candidateQuotes, recentQuotes);
        }
      }
    }
    if (!chosenQuote) {
      chosenQuote = getRandomQuoteFromList(quotes, recentQuotes);
    }
    const newRecentQuotes = [chosenQuote._id, ...recentQuotes].slice(0, 2);
    localStorage.setItem('quoteOfTheDayV2', JSON.stringify({
      quote: chosenQuote,
      date: today,
      recentQuotes: newRecentQuotes
    }));
    setRandomQuote(chosenQuote);
  }

  const formatTags = (tags: string) => {
    if (!tags) return '';
    return tags.split(',')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0)
      .map(tag => tag.startsWith('#') ? tag : `#${tag}`)
      .join(',');
  };

  const handleCreateQuote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAuthenticated || !user) {
      toast.error('Please login to create quotes')
      return
    }

    if (!newQuote.quote || !newQuote.author) {
      toast.error('Quote and author fields are required')
      return
    }

    try {
      await quotesAPI.createQuote({
        quote: newQuote.quote,
        author: newQuote.author,
        tags: formatTags(newQuote.tags),
        user_id: user.id,
        user_name: user.name,
        likes: 0,
        dislikes: 0,
        is_active: true
      })
      toast.success('Quote created successfully!')
      setNewQuote({ quote: '', author: '', tags: '' })
      fetchQuotes()
    } catch (err) {
      console.error('Create quote error:', err)
      toast.error('Failed to create quote')
    }
  }

  const handleLikeQuote = async (id: string) => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to like quotes')
      return
    }

    // Find the quote to check if it belongs to the current user
    const quote = quotes.find(q => q._id === id)
    if (quote?.user_id === user.id) {
      toast.error('You cannot like your own quotes')
      return
    }

    try {
      await quotesAPI.likeQuote(id)
      fetchQuotes()
    } catch (err) {
      console.error('Like quote error:', err)
      toast.error('Failed to like quote')
    }
  }

  const handleDislikeQuote = async (id: string) => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to dislike quotes')
      return
    }

    // Find the quote to check if it belongs to the current user
    const quote = quotes.find(q => q._id === id)
    if (quote?.user_id === user.id) {
      toast.error('You cannot dislike your own quotes')
      return
    }

    try {
      await quotesAPI.dislikeQuote(id)
      fetchQuotes()
    } catch (err) {
      console.error('Dislike quote error:', err)
      toast.error('Failed to dislike quote')
    }
  }

  const handleEditQuote = async () => {
    if (!editingQuote || !user) return

    if (!editingQuote.quote || !editingQuote.author) {
      toast.error('Quote and author fields are required')
      return
    }

    try {
      await quotesAPI.updateQuote(editingQuote._id, { 
        quote: editingQuote.quote,
        author: editingQuote.author,
        tags: formatTags(editingQuote.tags || '')
      })
      toast.success('Quote updated successfully!')
      setIsEditDialogOpen(false)
      setEditingQuote(null)
      fetchQuotes()
    } catch (err) {
      console.error('Update quote error:', err)
      toast.error('Failed to update quote')
    }
  }

  const handleDeleteQuote = async (id: string) => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to delete quotes')
      return
    }

    try {
      await quotesAPI.deleteQuote(id)
      toast.success('Quote deleted successfully!')
      setIsDeleteDialogOpen(false)
      setQuoteToDelete(null)
      fetchQuotes()
    } catch (err) {
      console.error('Delete quote error:', err)
      toast.error('Failed to delete quote')
    }
  }

  const handleLogout = () => {
    useAuthStore.getState().logout()
    router.push('/login')
  }

  // Filter quotes to only show user's own quotes in the manage tab
  const userQuotes = quotes.filter(quote => quote.user_id === user?.id)

  // Filter quotes based on search and filter type
  const filteredQuotes = quotes.filter(quote => {
    const searchTerm = quoteSearch.toLowerCase();
    if (!searchTerm) return true;

    switch (searchFilter) {
      case 'quotes':
        return quote.quote?.toLowerCase().includes(searchTerm);
      case 'authors':
        return quote.author.toLowerCase().includes(searchTerm);
      case 'tags':
        return quote.tags?.toLowerCase().includes(searchTerm);
      case 'all':
      default:
        return (
          quote.quote?.toLowerCase().includes(searchTerm) ||
          quote.author.toLowerCase().includes(searchTerm) ||
          quote.tags?.toLowerCase().includes(searchTerm)
        );
    }
  });

  // Calculate quotes pagination
  const totalQuotesPages = Math.ceil(filteredQuotes.length / ITEMS_PER_PAGE)
  const paginatedQuotes = filteredQuotes.slice(
    (quotesPage - 1) * ITEMS_PER_PAGE,
    quotesPage * ITEMS_PER_PAGE
  )

  // Filter authors based on search
  const filteredAuthors = authors
    .filter(author =>
      author.toLowerCase().includes(authorSearch.toLowerCase())
    )
    .sort((a, b) => a.localeCompare(b));

  // Calculate authors pagination
  const totalAuthorsPages = Math.ceil(filteredAuthors.length / ITEMS_PER_PAGE)
  const paginatedAuthors = filteredAuthors.slice(
    (authorsPage - 1) * ITEMS_PER_PAGE,
    authorsPage * ITEMS_PER_PAGE
  )

  // Reset pagination when search changes
  useEffect(() => {
    setQuotesPage(1)
  }, [quoteSearch])

  useEffect(() => {
    setAuthorsPage(1)
  }, [authorSearch])

  // Pagination component
  const Pagination = ({ currentPage, totalPages, onPageChange }: { 
    currentPage: number, 
    totalPages: number, 
    onPageChange: (page: number) => void 
  }) => {
    const baseButtonStyles = "join-item btn min-h-8 h-8 min-w-8 w-8 px-0 text-sm font-medium border shadow-sm rounded-md transition-colors duration-200"
    const normalButtonStyles = `${baseButtonStyles} bg-white hover:bg-gray-50 text-gray-700 hover:text-gray-900 border-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 dark:hover:text-white dark:border-gray-600`
    const activeButtonStyles = `${baseButtonStyles} bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100 hover:text-blue-700 dark:bg-blue-900 dark:text-blue-200 dark:border-blue-800 dark:hover:bg-blue-800`
    const disabledButtonStyles = `${baseButtonStyles} bg-gray-50 text-gray-300 cursor-not-allowed hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-600 dark:border-gray-700`

    const effectiveTotalPages = Math.max(1, totalPages)
    const effectiveCurrentPage = Math.min(currentPage, effectiveTotalPages)

    return (
      <div className="join flex justify-center items-center mt-8 gap-1.5">
        {/* First Page */}
        <button
          className={effectiveCurrentPage === 1 ? disabledButtonStyles : normalButtonStyles}
          onClick={() => onPageChange(1)}
          disabled={effectiveCurrentPage === 1}
          title="First Page"
        >
          «
        </button>
        
        {/* Previous Page */}
        <button
          className={effectiveCurrentPage === 1 ? disabledButtonStyles : normalButtonStyles}
          onClick={() => onPageChange(effectiveCurrentPage - 1)}
          disabled={effectiveCurrentPage === 1}
          title="Previous Page"
        >
          ‹
        </button>

        {/* Page Numbers */}
        <div className="join flex gap-1.5">
          {Array.from({ length: Math.min(5, Math.max(1, effectiveTotalPages)) }, (_, i) => {
            let pageNum;
            if (effectiveTotalPages <= 5) {
              pageNum = i + 1;
            } else if (effectiveCurrentPage <= 3) {
              pageNum = i + 1;
            } else if (effectiveCurrentPage >= effectiveTotalPages - 2) {
              pageNum = effectiveTotalPages - 4 + i;
            } else {
              pageNum = effectiveCurrentPage - 2 + i;
            }

            const isActive = effectiveCurrentPage === pageNum;
            
            return (
              <button
                key={pageNum}
                className={isActive ? activeButtonStyles : normalButtonStyles}
                onClick={() => onPageChange(pageNum)}
                title={`Page ${pageNum}`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        {/* Next Page */}
        <button
          className={effectiveCurrentPage === effectiveTotalPages ? disabledButtonStyles : normalButtonStyles}
          onClick={() => onPageChange(effectiveCurrentPage + 1)}
          disabled={effectiveCurrentPage === effectiveTotalPages}
          title="Next Page"
        >
          ›
        </button>

        {/* Last Page */}
        <button
          className={effectiveCurrentPage === effectiveTotalPages ? disabledButtonStyles : normalButtonStyles}
          onClick={() => onPageChange(effectiveTotalPages)}
          disabled={effectiveCurrentPage === effectiveTotalPages}
          title="Last Page"
        >
          »
        </button>
      </div>
    );
  };

  // Handle author click to filter quotes
  const handleAuthorClick = (author: string) => {
    setQuoteSearch(author)
    setSearchFilter('authors')
    setActiveTab('quotes')
  }

  // Add character count display helper
  const remainingCharacters = MAX_QUOTE_LENGTH - (newQuote.quote?.length || 0)

  // Add character count display helper for edit dialog
  const editingCharactersRemaining = editingQuote 
    ? MAX_QUOTE_LENGTH - (editingQuote.quote?.length || 0)
    : MAX_QUOTE_LENGTH;

  const handleShowReactions = async (quoteId: string) => {
    if (!isAuthenticated || !user) {
      toast.error('Please login to view reactions')
      return
    }

    setSelectedQuoteId(quoteId)
    setIsReactionsDialogOpen(true)
    setReactionsLoading(true)

    try {
      const data = await quotesAPI.getQuoteReactions(quoteId)
      setReactions(data)
    } catch (err) {
      console.error('Get reactions error:', err)
      toast.error('Failed to load reactions')
    } finally {
      setReactionsLoading(false)
    }
  }

  // Filter userQuotes by quote text or tags (case-insensitive)
  const filteredUserQuotes = userQuotes.filter(q => {
    const search = quoteSearch.trim().toLowerCase()
    if (!search) return true
    return (
      q.quote?.toLowerCase().includes(search) ||
      (q.tags?.toLowerCase().includes(search))
    )
  })

  // For My Quotes tab
  const likedQuotes = quotes.filter(q => q.is_liked)
  const dislikedQuotes = quotes.filter(q => q.is_disliked)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="bg-background/80 border-b border-border shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Quote System</h1>
          <div className="flex gap-4 items-center">
            <ThemeToggle />
            {isAuthenticated ? (
              <>
                <span className="text-gray-600">
                  Hello, <span className="font-bold">{user?.name?.split(' ')[0]}</span>
                </span>
                <Button
                  key="logout"
                  variant="destructive"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  key="login"
                  variant="outline"
                  onClick={() => router.push('/login')}
                >
                  Login
                </Button>
                <Button
                  key="register"
                  onClick={() => router.push('/register')}
                >
                  Register
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="home">Home</TabsTrigger>
            <TabsTrigger value="quotes">Quotes</TabsTrigger>
            <TabsTrigger value="authors">Authors</TabsTrigger>
            {isAuthenticated && <TabsTrigger value="manage">Manage</TabsTrigger>}
            {isAuthenticated && <TabsTrigger value="myquotes">My Quotes</TabsTrigger>}
          </TabsList>

          <TabsContent value="home">
            <Card className="w-full">
              <CardContent className="pt-6">
                <div className="text-center space-y-6">
                  <h2 className="text-3xl font-bold mb-4 text-foreground dark:text-white">Quote of the Day</h2>
                  {randomQuote ? (
                    <>
                      <p className="text-2xl font-medium italic">"{randomQuote.quote}"</p>
                      <p className="text-lg text-gray-600">- {randomQuote.author}</p>
                      <Button onClick={handleNewRandomQuote} variant="outline">
                        Get Another Quote
                      </Button>
                    </>
                  ) : (
                    <div className="text-center text-gray-500">
                      No quotes available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="quotes">
            <div className="mb-6 flex gap-4 items-center">
              <Select
                value={searchFilter}
                onValueChange={setSearchFilter}
              >
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Filter by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="quotes">Quotes</SelectItem>
                  <SelectItem value="authors">Authors</SelectItem>
                  <SelectItem value="tags">Tags</SelectItem>
                </SelectContent>
              </Select>
              <div className="relative flex-1 max-w-md">
                <Input
                  type="text"
                  placeholder={`Search ${searchFilter === 'all' ? 'quotes, authors or tags' : searchFilter}...`}
                  value={quoteSearch}
                  onChange={(e) => setQuoteSearch(e.target.value)}
                  className="pr-8"
                />
                {quoteSearch && (
                  <button
                    onClick={() => setQuoteSearch('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
            {loading ? (
              <div className="text-center">Loading quotes...</div>
            ) : filteredQuotes.length === 0 ? (
              <div className="text-center text-gray-500">
                {quoteSearch ? 'No quotes found' : 'No quotes available'}
              </div>
            ) : (
              <>
                <div data-testid="quotes-list" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {paginatedQuotes.map((quote) => (
                    <Card key={quote._id} className="relative">
                      <CardContent className="pt-6">
                        {activeTab === 'quotes' && quote.user_id === user?.id && (
                          <div className="absolute top-2 right-2">
                            <User className="h-5 w-5 text-primary" />
                          </div>
                        )}
                        <div className="flex flex-col gap-2 min-h-[120px]">
                          <p className="text-lg font-medium">{quote.quote}</p>
                          <p className="text-sm text-gray-600">- {quote.author}</p>
                          {quote.tags && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {quote.tags.split(',').map((tag, index) => (
                                <span key={index} className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full">
                                  {tag.trim()}
                                </span>
                              ))}
                            </div>
                          )}
                          {quote.user_name && (
                            <p className="text-xs text-gray-500">Uploaded by {quote.user_name}</p>
                          )}
                        </div>
                        <div className="absolute bottom-4 right-4 flex items-center gap-2 mt-4">
                          <Button
                            data-testid="quote-like-button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleLikeQuote(quote._id)}
                            disabled={!isAuthenticated || quote.user_id === user?.id}
                            className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm ${
                              !isAuthenticated || quote.user_id === user?.id
                                ? 'bg-gray-100 text-gray-400'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            {quote.is_liked ? '❤️' : '🤍'} {quote.likes}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDislikeQuote(quote._id)}
                            className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm transition-colors ${
                              quote.user_id === user?.id
                                ? 'bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600'
                                : quote.is_disliked 
                                  ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                            disabled={quote.user_id === user?.id}
                          >
                            {quote.is_disliked ? '👎' : '👎'} {quote.dislikes}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleShowReactions(quote._id)}
                            className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-gray-100 text-gray-600 hover:bg-gray-200"
                          >
                            <ChevronUp className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                <Pagination
                  currentPage={quotesPage}
                  totalPages={totalQuotesPages}
                  onPageChange={setQuotesPage}
                />
              </>
            )}
          </TabsContent>

          <TabsContent value="authors">
            <div className="mb-6 relative max-w-md">
              <Input
                type="text"
                placeholder="Search authors..."
                value={authorSearch}
                onChange={(e) => setAuthorSearch(e.target.value)}
                className="pr-8"
              />
              {authorSearch && (
                <button
                  onClick={() => setAuthorSearch('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            {loading ? (
              <div className="text-center">Loading authors...</div>
            ) : filteredAuthors.length === 0 ? (
              <div className="text-center text-gray-500">
                {authorSearch ? 'No authors found' : 'No authors available'}
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {paginatedAuthors.map((author, index) => (
                    <Card 
                      key={`author-${author}-${index}`} 
                      className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => handleAuthorClick(author)}
                    >
                      <CardContent className="p-4">
                        <h3 className="text-base font-medium">{author}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {quotes.filter(quote => quote.author === author).length} quotes
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                <Pagination
                  currentPage={authorsPage}
                  totalPages={totalAuthorsPages}
                  onPageChange={setAuthorsPage}
                />
              </>
            )}
          </TabsContent>

          {isAuthenticated && (
            <TabsContent value="manage" className="space-y-4">
              <div data-testid="manage-tab-content" className="space-y-4">
                {!isAuthenticated ? (
                  <div className="text-center text-gray-500">Please login to manage your quotes</div>
                ) : (
                  <>
                    <div className="flex items-center gap-4">
                      <Button data-testid="add-quote-button" onClick={() => setIsNewQuoteDialogOpen(true)}>
                        Add New Quote
                      </Button>
                      <div className="relative flex-1">
                        <Input
                          data-testid="quote-text-input"
                          placeholder="Search my quotes or tags..."
                          value={quoteSearch}
                          onChange={(e) => setQuoteSearch(e.target.value)}
                          className="pr-8"
                        />
                        <Input
                          data-testid="author-input"
                          placeholder="Author"
                          value={authorSearch}
                          onChange={(e) => setAuthorSearch(e.target.value)}
                          className="pr-8 mt-2"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredUserQuotes.length === 0 ? (
                        <div className="col-span-full text-center text-gray-500">
                          You haven't created any quotes yet
                        </div>
                      ) : (
                        filteredUserQuotes.map((quote) => (
                          <Card key={quote._id} className="relative">
                            <CardContent className="pt-6">
                              <div className="flex flex-col gap-2">
                                <p className="text-lg font-medium">{quote.quote}</p>
                                <p className="text-sm text-gray-600">- {quote.author}</p>
                                {quote.tags && (
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {quote.tags.split(',').map((tag, index) => (
                                      <span key={index} className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full">
                                        {tag.trim()}
                                      </span>
                                    ))}
                                  </div>
                                )}
                                <p className="text-xs text-gray-500">Uploaded by {quote.user_name}</p>
                              </div>
                              <div className="absolute bottom-4 right-4 flex gap-2">
                                <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                  {quote.is_liked ? '❤️' : '🤍'} {quote.likes}
                                </span>
                                <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                  {quote.is_disliked ? '👎' : '👎'} {quote.dislikes}
                                </span>
                              </div>
                              <div className="absolute top-2 right-2 flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setEditingQuote(quote)
                                    setIsEditDialogOpen(true)
                                  }}
                                >
                                  Edit
                                </Button>
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => {
                                    setQuoteToDelete(quote._id)
                                    setIsDeleteDialogOpen(true)
                                  }}
                                >
                                  Delete
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        ))
                      )}
                    </div>
                  </>
                )}
              </div>
            </TabsContent>
          )}

          {isAuthenticated && (
            <TabsContent value="myquotes" className="space-y-4">
              <Tabs value={myQuotesSubTab} onValueChange={setMyQuotesSubTab} className="space-y-4">
                <TabsList className="flex justify-center">
                  <TabsTrigger value="my">My Quotes ({userQuotes.length})</TabsTrigger>
                  <TabsTrigger value="liked">Liked Quotes ({likedQuotes.length})</TabsTrigger>
                  <TabsTrigger value="disliked">Disliked Quotes ({dislikedQuotes.length})</TabsTrigger>
                </TabsList>
                <TabsContent value="my">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {userQuotes.length === 0 ? (
                      <div className="col-span-full text-center text-gray-500">You haven't created any quotes yet</div>
                    ) : (
                      userQuotes.map((quote) => (
                        <Card key={quote._id} className="relative">
                          <CardContent className="pt-6">
                            <div className="flex flex-col gap-2">
                              <p className="text-lg font-medium">{quote.quote}</p>
                              <p className="text-sm text-gray-600">- {quote.author}</p>
                              {quote.tags && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {quote.tags.split(',').map((tag, index) => (
                                    <span key={index} className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full">
                                      {tag.trim()}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <p className="text-xs text-gray-500">Uploaded by {quote.user_name}</p>
                            </div>
                            <div className="absolute bottom-4 right-4 flex gap-2">
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_liked ? '❤️' : '🤍'} {quote.likes}
                              </span>
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_disliked ? '👎' : '👎'} {quote.dislikes}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="liked">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {likedQuotes.length === 0 ? (
                      <div className="col-span-full text-center text-gray-500">You haven't liked any quotes yet</div>
                    ) : (
                      likedQuotes.map((quote) => (
                        <Card key={quote._id} className="relative">
                          <CardContent className="pt-6">
                            <div className="flex flex-col gap-2">
                              <p className="text-lg font-medium">{quote.quote}</p>
                              <p className="text-sm text-gray-600">- {quote.author}</p>
                              {quote.tags && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {quote.tags.split(',').map((tag, index) => (
                                    <span key={index} className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full">
                                      {tag.trim()}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <p className="text-xs text-gray-500">Uploaded by {quote.user_name}</p>
                            </div>
                            <div className="absolute bottom-4 right-4 flex gap-2">
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_liked ? '❤️' : '🤍'} {quote.likes}
                              </span>
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_disliked ? '👎' : '👎'} {quote.dislikes}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="disliked">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {dislikedQuotes.length === 0 ? (
                      <div className="col-span-full text-center text-gray-500">You haven't disliked any quotes yet</div>
                    ) : (
                      dislikedQuotes.map((quote) => (
                        <Card key={quote._id} className="relative">
                          <CardContent className="pt-6">
                            <div className="flex flex-col gap-2">
                              <p className="text-lg font-medium">{quote.quote}</p>
                              <p className="text-sm text-gray-600">- {quote.author}</p>
                              {quote.tags && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {quote.tags.split(',').map((tag, index) => (
                                    <span key={index} className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full">
                                      {tag.trim()}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <p className="text-xs text-gray-500">Uploaded by {quote.user_name}</p>
                            </div>
                            <div className="absolute bottom-4 right-4 flex gap-2">
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_liked ? '❤️' : '🤍'} {quote.likes}
                              </span>
                              <span className="flex items-center gap-1 px-2 py-1 rounded-full text-sm bg-transparent text-gray-600 cursor-default border-none shadow-none hover:bg-transparent hover:text-gray-600">
                                {quote.is_disliked ? '👎' : '👎'} {quote.dislikes}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </TabsContent>
          )}
        </Tabs>

        {/* Edit Quote Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Edit Quote</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-quote">Quote Text</Label>
                <div className="relative">
                  <Textarea
                    id="edit-quote"
                    value={editingQuote?.quote || ''}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value.length <= MAX_QUOTE_LENGTH && editingQuote) {
                        setEditingQuote({
                          ...editingQuote,
                          quote: value
                        });
                      }
                    }}
                    maxLength={MAX_QUOTE_LENGTH}
                    className="resize-none w-full max-w-[450px] h-32"
                    placeholder="Enter quote text"
                    required
                  />
                  <div className={`text-sm mt-1 text-right ${
                    editingCharactersRemaining <= 20 
                      ? 'text-red-500 dark:text-red-400' 
                      : editingCharactersRemaining <= 50 
                        ? 'text-yellow-500 dark:text-yellow-400' 
                        : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {editingCharactersRemaining} characters remaining
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-author">Author</Label>
                <Input
                  id="edit-author"
                  value={editingQuote?.author || ''}
                  onChange={(e) => setEditingQuote(prev => prev ? { ...prev, author: e.target.value } : null)}
                  placeholder="Enter author name"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-tags">Tags (optional)</Label>
                <Input
                  id="edit-tags"
                  value={editingQuote?.tags || ''}
                  onChange={(e) => setEditingQuote(prev => prev ? { ...prev, tags: e.target.value } : null)}
                  placeholder="Enter tags separated by commas (e.g., inspiration, life, success)"
                />
                <p className="text-xs text-gray-500">Tags will automatically be formatted with #</p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleEditQuote}>
                Save Changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Quote</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <p className="text-base">Are you sure?</p>
              <p className="text-sm text-gray-500">You will not be able to recover this quote!</p>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setIsDeleteDialogOpen(false)
                setQuoteToDelete(null)
              }}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => quoteToDelete && handleDeleteQuote(quoteToDelete)}
              >
                Delete
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Reactions Dialog */}
        <Dialog open={isReactionsDialogOpen} onOpenChange={setIsReactionsDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Quote Reactions</DialogTitle>
            </DialogHeader>
            <Tabs defaultValue="likes" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="likes">Likes ({reactions.likes.length})</TabsTrigger>
                <TabsTrigger value="dislikes">Dislikes ({reactions.dislikes.length})</TabsTrigger>
              </TabsList>
              <TabsContent value="likes" className="mt-4">
                {reactionsLoading ? (
                  <div className="text-center py-4">Loading reactions...</div>
                ) : reactions.likes.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">No likes yet</div>
                ) : (
                  <div className="space-y-2">
                    {reactions.likes.map((name, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-foreground">{name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>
              <TabsContent value="dislikes" className="mt-4">
                {reactionsLoading ? (
                  <div className="text-center py-4">Loading reactions...</div>
                ) : reactions.dislikes.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">No dislikes yet</div>
                ) : (
                  <div className="space-y-2">
                    {reactions.dislikes.map((name, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
                        <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-foreground">{name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>

        {/* Add New Quote Dialog */}
        <Dialog open={isNewQuoteDialogOpen} onOpenChange={setIsNewQuoteDialogOpen}>
          <DialogContent className="max-w-2xl w-full">
            <DialogHeader>
              <DialogTitle>Add New Quote</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateQuote} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="quote">Quote</Label>
                <Textarea
                  id="quote"
                  placeholder="Enter your quote"
                  value={newQuote.quote}
                  onChange={(e) => {
                    setNewQuote(prev => ({ ...prev, quote: e.target.value }))
                    setQuoteCharCount(e.target.value.length)
                  }}
                  required
                  maxLength={MAX_QUOTE_LENGTH}
                  className="h-32 resize-none overflow-y-auto break-all overflow-x-hidden w-full"
                />
                <div className={`text-sm mt-1 text-right ${
                  MAX_QUOTE_LENGTH - (newQuote.quote?.length || 0) <= 20
                    ? 'text-red-500'
                    : MAX_QUOTE_LENGTH - (newQuote.quote?.length || 0) <= 50
                    ? 'text-yellow-500'
                    : 'text-gray-500'
                }`}>
                  {MAX_QUOTE_LENGTH - (newQuote.quote?.length || 0)} characters remaining
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="author">Author</Label>
                <Input
                  id="author"
                  placeholder="Enter author name"
                  value={newQuote.author}
                  onChange={(e) => setNewQuote(prev => ({ ...prev, author: e.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tags">Tags (optional)</Label>
                <Input
                  id="tags"
                  placeholder="Enter tags separated by commas (e.g., inspiration, life, success)"
                  value={newQuote.tags}
                  onChange={(e) => setNewQuote(prev => ({ ...prev, tags: e.target.value }))}
                />
                <p className="text-xs text-gray-500">Tags will automatically be formatted with #</p>
              </div>
              <DialogFooter>
                <Button type="submit">Add Quote</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </main>
    </div>
  )
}