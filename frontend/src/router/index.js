import { createRouter, createWebHistory } from 'vue-router';
import BooksPage from '../pages/BooksPage.vue';
import BookDetailsPage from '../pages/BookDetailsPage.vue';
import AboutPage from '../pages/AboutPage.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/books' },
    { path: '/books', name: 'books', component: BooksPage },
    { path: '/books/:id', name: 'book-details', component: BookDetailsPage, props: true },
    { path: '/about', name: 'about', component: AboutPage },
  ],
});

export default router;
