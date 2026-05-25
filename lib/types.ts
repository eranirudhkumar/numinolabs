export interface Book {
  id: string;
  isbn: string | null;
  title: string;
  author: string;
  genre: string | null;
  published_year: number | null;
  total_copies: number;
  available_copies: number;
  created_at: string;
  updated_at: string;
}

export interface BookCreate {
  isbn?: string;
  title: string;
  author: string;
  genre?: string;
  published_year?: number;
  total_copies?: number;
}

export interface BookUpdate {
  isbn?: string;
  title?: string;
  author?: string;
  genre?: string;
  published_year?: number;
  total_copies?: number;
}

export interface PaginatedBooks {
  books: Book[];
  total: number;
  page: number;
  page_size: number;
}

export type MembershipStatus = "active" | "suspended" | "expired";

export interface Member {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  address: string | null;
  membership_status: MembershipStatus;
  membership_date: string;
  created_at: string;
  updated_at: string;
}

export interface MemberCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  address?: string;
}

export interface MemberUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  address?: string;
  membership_status?: MembershipStatus;
}

export interface PaginatedMembers {
  members: Member[];
  total: number;
  page: number;
  page_size: number;
}

export type LoanStatus = "active" | "returned" | "overdue";

export interface Loan {
  id: string;
  book_id: string;
  member_id: string;
  book: Book;
  member: Member;
  status: LoanStatus;
  fine_amount: number;
  borrowed_at: string;
  due_date: string;
  returned_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BorrowRequest {
  book_id: string;
  member_id: string;
}

export interface LoanListResponse {
  loans: Loan[];
  total: number;
}
