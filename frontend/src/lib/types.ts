export interface Quote {
  _id: string;
  quote: string;
  author: string;
  tags?: string;
  likes: number;
  dislikes: number;
  is_active: boolean;
  user_id: string;
  user_name: string;
  created_at: string;
  updated_at: string;
  is_liked?: boolean;
} 