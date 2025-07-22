import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
  theme_preference: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  rememberMe: boolean
  login: (user: User, token: string, rememberMe: boolean) => void
  logout: () => void
  updateTheme: (theme: string) => void
}

// Helper to safely access storage only in the browser
declare const window: any;
const getSessionStorage = () => (typeof window !== 'undefined' ? window.sessionStorage : undefined)
const getLocalStorage = () => (typeof window !== 'undefined' ? window.localStorage : undefined)

// No-op storage for SSR
const noopStorage = {
  getItem: (_: string) => null,
  setItem: (_: string, __: string) => {},
  removeItem: (_: string) => {},
}

// Create separate stores for session and persistent storage
const createAuthStore = (storage: Storage | undefined) => 
  create<AuthState>()(
    persist(
      (set) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        rememberMe: false,
        login: (user: User, token: string, rememberMe: boolean) => {
          if (!token) {
            console.error('No token provided during login')
            return
          }
          set({ user, token, isAuthenticated: true, rememberMe })
        },
        logout: () => {
          set({ user: null, token: null, isAuthenticated: false, rememberMe: false })
        },
        updateTheme: (theme) => set((state) => ({
          user: state.user ? { ...state.user, theme_preference: theme } : null
        }))
      }),
      {
        name: 'auth-storage',
        storage: createJSONStorage(() => storage ?? noopStorage),
        skipHydration: true,
      }
    )
  )

// Create both stores
export const useSessionAuthStore = createAuthStore(getSessionStorage())
export const usePersistentAuthStore = createAuthStore(getLocalStorage())

// Export a unified store that uses the appropriate storage based on rememberMe
export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  rememberMe: false,
  login: (user: User, token: string, rememberMe: boolean) => {
    if (rememberMe) {
      usePersistentAuthStore.getState().login(user, token, rememberMe)
    } else {
      useSessionAuthStore.getState().login(user, token, rememberMe)
    }
    set({ user, token, isAuthenticated: true, rememberMe })
  },
  logout: () => {
    useSessionAuthStore.getState().logout()
    usePersistentAuthStore.getState().logout()
    set({ user: null, token: null, isAuthenticated: false, rememberMe: false })
  },
  updateTheme: (theme) => {
    const state = get()
    if (state.user) {
      const newUser = { ...state.user, theme_preference: theme }
      if (state.rememberMe) {
        usePersistentAuthStore.getState().updateTheme(theme)
      } else {
        useSessionAuthStore.getState().updateTheme(theme)
      }
      set({ user: newUser })
    }
  }
})) 