import axios from "axios";
import type {
  Book,
  BookCreate,
  BookUpdate,
  BorrowRequest,
  Loan,
  LoanListResponse,
  Member,
  MemberCreate,
  MemberUpdate,
  PaginatedBooks,
  PaginatedLoans,
  PaginatedMembers,
} from "./types";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

export const bookApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    title?: string;
    author?: string;
    genre?: string;
  }) => api.get<PaginatedBooks>("/books", { params }).then((r) => r.data),

  get: (id: string) => api.get<Book>(`/books/${id}`).then((r) => r.data),

  create: (data: BookCreate) =>
    api.post<Book>("/books", data).then((r) => r.data),

  update: (id: string, data: BookUpdate) =>
    api.patch<Book>(`/books/${id}`, data).then((r) => r.data),
};

export const memberApi = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    api.get<PaginatedMembers>("/members", { params }).then((r) => r.data),

  get: (id: string) => api.get<Member>(`/members/${id}`).then((r) => r.data),

  create: (data: MemberCreate) =>
    api.post<Member>("/members", data).then((r) => r.data),

  update: (id: string, data: MemberUpdate) =>
    api.patch<Member>(`/members/${id}`, data).then((r) => r.data),
};

export const loanApi = {
  list: (params?: { page?: number; page_size?: number }) =>
    api.get<PaginatedLoans>("/loans", { params }).then((r) => r.data),

  borrow: (data: BorrowRequest) =>
    api.post<Loan>("/loans/borrow", data).then((r) => r.data),

  return: (loanId: string) =>
    api.post<Loan>(`/loans/${loanId}/return`).then((r) => r.data),

  byMember: (memberId: string, activeOnly = false) =>
    api
      .get<LoanListResponse>(`/loans/member/${memberId}`, {
        params: { active_only: activeOnly },
      })
      .then((r) => r.data),

  overdue: () =>
    api.get<LoanListResponse>("/loans/overdue").then((r) => r.data),
};

export default api;
