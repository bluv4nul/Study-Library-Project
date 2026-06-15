import { createRouter, createWebHistory } from "vue-router";
import BooksPage from "../pages/BooksPage.vue";
import BookDetailsPage from "../pages/BookDetailsPage.vue";
import AuthorsPage from "../pages/AuthorsPage.vue";
import GenresPage from "../pages/GenresPage.vue";
import PublishersPage from "../pages/PublishersPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/books" },
    { path: "/books", name: "books", component: BooksPage },
    {
      path: "/books/:id",
      name: "book-details",
      component: BookDetailsPage,
      props: true,
    },
    { path: "/authors", name: "authors", component: AuthorsPage },
    { path: "/genres", name: "genres", component: GenresPage },
    { path: "/publishers", name: "publishers", component: PublishersPage },
  ],
});

export default router;
