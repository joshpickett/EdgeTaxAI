// Blog post data (in a real application, this would come from a backend)
const blogPosts = [
    {
        id: 1,
        title: 'How to Optimize Taxes for Gig Workers',
        excerpt: 'A quick guide to maximizing deductions for gig workers and expats...',
        date: 'January 1, 2024',
        image: 'images/blog-post1.jpg'
    },
    // Add more blog posts here
];

const POSTS_PER_PAGE = 6;
let currentPage = 1;
let filteredPosts = [...blogPosts];

// Search functionality
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');

function performSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    filteredPosts = blogPosts.filter(post => 
        post.title.toLowerCase().includes(searchTerm) ||
        post.excerpt.toLowerCase().includes(searchTerm)
    );
    currentPage = 1;
    renderPosts();
    updatePagination();
}

searchInput.addEventListener('input', performSearch);
searchButton.addEventListener('click', performSearch);

// Pagination functionality
function renderPosts() {
    const startIndex = (currentPage - 1) * POSTS_PER_PAGE;
    const endIndex = startIndex + POSTS_PER_PAGE;
    const postsToShow = filteredPosts.slice(startIndex, endIndex);

    const blogGrid = document.querySelector('.blog-grid');
    blogGrid.innerHTML = postsToShow.map(post => `
        <article class="blog-card">
            <div class="blog-image">
                <img src="${post.image}" alt="${post.title}">
            </div>
            <div class="blog-content">
                <h3><a href="blog-post${post.id}.html">${post.title}</a></h3>
                <p>${post.excerpt}</p>
                <span class="post-date">${post.date}</span>
            </div>
        </article>
    `).join('');
}

function updatePagination() {
    const totalPages = Math.ceil(filteredPosts.length / POSTS_PER_PAGE);
    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.classList.add('pagination-btn');
        if (i === currentPage) pageButton.classList.add('active');
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            currentPage = i;
            renderPosts();
            updatePagination();
        });
        pageNumbers.appendChild(pageButton);
    }

    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
}

// Event listeners for pagination buttons
document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderPosts();
        updatePagination();
    }
});

document.getElementById('nextPage').addEventListener('click', () => {
    const totalPages = Math.ceil(filteredPosts.length / POSTS_PER_PAGE);
    if (currentPage < totalPages) {
        currentPage++;
        renderPosts();
        updatePagination();
    }
});

// Initial render
renderPosts();
updatePagination();
