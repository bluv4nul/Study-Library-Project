db = db.getSiblingDB("electrolibrary");

const seed = [
  {
    collection: "authors",
    documents: [
      {
        ref: "orwell",
        author_name: "George Orwell",
        author_nickname: null,
        email: "orwell@mail.com",
        social_media_link: "https://twitter.com/georgeorwell",
      },
      {
        ref: "huxley",
        author_name: "Aldous Huxley",
        author_nickname: null,
        email: "huxley@mail.com",
        social_media_link: "https://www.example.com/aldous-huxley",
      },
      {
        ref: "tolkien",
        author_name: "J.R.R. Tolkien",
        author_nickname: "Tolkien",
        email: "tolkien@mail.com",
        social_media_link: "https://www.example.com/jrr-tolkien",
      },
      {
        ref: "gaiman",
        author_name: "Neil Gaiman",
        author_nickname: "The Sandman",
        email: "gaiman@mail.com",
        social_media_link: "https://twitter.com/neilhimself",
      },
      {
        ref: "pratchett",
        author_name: "Terry Pratchett",
        author_nickname: null,
        email: "pratchett@mail.com",
        social_media_link: "https://www.example.com/terry-pratchett",
      },
    ],
  },
  {
    collection: "genres",
    documents: [
      {
        ref: "dystopia",
        genre_name: "Dystopia",
      },
      {
        ref: "science_fiction",
        genre_name: "Science Fiction",
      },
      {
        ref: "fantasy",
        genre_name: "Fantasy",
      },
      {
        ref: "satire",
        genre_name: "Satire",
      },
      {
        ref: "adventure",
        genre_name: "Adventure",
      },
      {
        ref: "comedy",
        genre_name: "Comedy",
      },
    ],
  },
  {
    collection: "publishers",
    documents: [
      {
        ref: "penguin",
        publisher_name: "Penguin Books",
        publisher_city: "London",
        email: "contact@penguin.co.uk",
        publisher_website: "https://www.penguin.co.uk",
      },
      {
        ref: "harpercollins",
        publisher_name: "HarperCollins",
        publisher_city: "New York",
        email: "info@harpercollins.com",
        publisher_website: "https://www.harpercollins.com",
      },
      {
        ref: "bloomsbury",
        publisher_name: "Bloomsbury",
        publisher_city: "London",
        email: "support@bloomsbury.com",
        publisher_website: "https://www.bloomsbury.com",
      },
    ],
  },
  {
    collection: "books",
    documents: [
      {
        title: "1984",
        year: 1949,
        isbn: "978-0-452-28423-4",
        author_refs: ["orwell"],
        genre_refs: ["dystopia", "science_fiction"],
        publisher_ref: "penguin",
      },
      {
        title: "Animal Farm",
        year: 1945,
        isbn: "978-0-452-28424-1",
        author_refs: ["orwell"],
        genre_refs: ["dystopia", "satire"],
        publisher_ref: "penguin",
      },
      {
        title: "Brave New World",
        year: 1932,
        isbn: "978-0-06-085052-4",
        author_refs: ["huxley"],
        genre_refs: ["dystopia", "science_fiction"],
        publisher_ref: "harpercollins",
      },
      {
        title: "The Hobbit",
        year: 1937,
        isbn: "978-0-618-00221-3",
        author_refs: ["tolkien"],
        genre_refs: ["fantasy", "adventure"],
        publisher_ref: "harpercollins",
      },
      {
        title: "Good Omens",
        year: 1990,
        isbn: "978-0-575-04826-3",
        author_refs: ["gaiman", "pratchett"],
        genre_refs: ["fantasy", "comedy"],
        publisher_ref: "bloomsbury",
      },
    ],
  },
];

const refMap = {};

for (const section of seed) {
  if (!section.collection || !Array.isArray(section.documents)) continue;
  if (section.collection === "books") continue;

  const docs = section.documents.map((doc) => {
    if (!doc.ref) return doc;

    const id = new ObjectId();
    refMap[`${section.collection}:${doc.ref}`] = id;
    const { ref, ...rest } = doc;
    return { ...rest, _id: id };
  });

  print(
    `Inserting ${docs.length} document(s) into collection ${section.collection}`,
  );
  db.getCollection(section.collection).insertMany(docs);
}

const booksSection = seed.find((section) => section.collection === "books");
if (booksSection && Array.isArray(booksSection.documents)) {
  const bookDocs = booksSection.documents.map((book) => {
    const doc = { ...book };

    if (Array.isArray(doc.author_refs)) {
      doc.author_ids = doc.author_refs.map((ref) => {
        const id = refMap[`authors:${ref}`];
        if (!id) throw new Error(`Unknown author ref: ${ref}`);
        return id;
      });
      delete doc.author_refs;
    }

    if (Array.isArray(doc.genre_refs)) {
      doc.genre_ids = doc.genre_refs.map((ref) => {
        const id = refMap[`genres:${ref}`];
        if (!id) throw new Error(`Unknown genre ref: ${ref}`);
        return id;
      });
      delete doc.genre_refs;
    }

    if (doc.publisher_ref) {
      const id = refMap[`publishers:${doc.publisher_ref}`];
      if (!id) throw new Error(`Unknown publisher ref: ${doc.publisher_ref}`);
      doc.publisher_id = id;
      delete doc.publisher_ref;
    }

    return doc;
  });

  print(`Inserting ${bookDocs.length} document(s) into collection books`);
  db.books.insertMany(bookDocs);
}

const indexes = [
  { col: "books", key: { title: 1 } },
  { col: "books", key: { isbn: 1 }, opts: { unique: true } },
  { col: "books", key: { year: 1 } },
  { col: "books", key: { publisher_id: 1 } },
  { col: "books", key: { author_ids: 1 } },
  { col: "books", key: { genre_ids: 1 } },
  { col: "books", key: { year: 1, title: 1 } },
  { col: "books", key: { publisher_id: 1, year: 1 } },
  { col: "authors", key: { author_name: 1 } },
  { col: "genres", key: { genre_name: 1 } },
  { col: "publishers", key: { publisher_name: 1 } },
];

for (const { col, key, opts } of indexes) {
  db.getCollection(col).createIndex(key, opts || {});
}

print("Seed loaded and indexes created.");
