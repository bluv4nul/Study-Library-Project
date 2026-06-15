import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 10000,
});

const unwrap = (response) => response.data;

export const normalizeId = (item) => item?._id || item?.id || "";

export const normalizeList = (payload) => {
  if (Array.isArray(payload)) return { items: payload, total: payload.length };
  const items =
    payload.items || payload.data || payload.results || payload.books || [];
  const total = payload.total || payload.count || items.length;
  return { items, total };
};

export const libraryApi = {
  async getBooks(params = {}) {
    return normalizeList(await api.get("/books", { params }).then(unwrap));
  },

  async getBook(id) {
    return api.get(`/books/${id}`).then(unwrap);
  },

  async createBook(data) {
    return api.post("/books", data).then(unwrap);
  },

  async updateBook(id, data) {
    return api.patch(`/books/${id}`, data).then(unwrap);
  },

  async deleteBook(id) {
    return api.delete(`/books/${id}`).then(unwrap);
  },

  async getAuthors(params = {}) {
    return normalizeList(
      await api
        .get("/authors", { params: { limit: 100, ...params } })
        .then(unwrap),
    );
  },

  async getGenres(params = {}) {
    return normalizeList(
      await api
        .get("/genres", { params: { limit: 100, ...params } })
        .then(unwrap),
    );
  },

  async getPublishers(params = {}) {
    return normalizeList(
      await api
        .get("/publishers", { params: { limit: 100, ...params } })
        .then(unwrap),
    );
  },

  // Authors CRUD
  async createAuthor(data) {
    return api.post("/authors", data).then(unwrap);
  },

  async updateAuthor(id, data) {
    return api.patch(`/authors/${id}`, data).then(unwrap);
  },

  async deleteAuthor(id) {
    return api.delete(`/authors/${id}`).then(unwrap);
  },

  // Genres CRUD
  async createGenre(data) {
    return api.post("/genres", data).then(unwrap);
  },

  async updateGenre(id, data) {
    return api.patch(`/genres/${id}`, data).then(unwrap);
  },

  async deleteGenre(id) {
    return api.delete(`/genres/${id}`).then(unwrap);
  },

  // Publishers CRUD
  async createPublisher(data) {
    return api.post("/publishers", data).then(unwrap);
  },

  async updatePublisher(id, data) {
    return api.patch(`/publishers/${id}`, data).then(unwrap);
  },

  async deletePublisher(id) {
    return api.delete(`/publishers/${id}`).then(unwrap);
  },
};
