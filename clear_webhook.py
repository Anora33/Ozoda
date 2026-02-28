<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Portfolio</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        header { background: #4A90E2; color: white; padding: 2rem; text-align: center; }
        h1 { margin: 0; }
        main { padding: 2rem; display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center; }
        .project { background: white; padding: 1rem; border-radius: 10px; width: 300px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .project h2 { margin-top: 0; color: #333; }
        .project p { color: #555; }
        .links a { margin-right: 1rem; text-decoration: none; color: #4A90E2; font-weight: bold; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <header>
        <h1>My Portfolio</h1>
    </header>
    <main id="projects">
        <!-- Loyiha kartochkalari shu yerga tushadi -->
    </main>

    <script>
        // Backend API URL
        const apiUrl = 'http://127.0.0.1:8000/api/projects/';

        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('projects');
                data.forEach(project => {
                    const card = document.createElement('div');
                    card.className = 'project';
                    card.innerHTML = `
                        <h2>${project.title}</h2>
                        <p>${project.description}</p>
                        <p><strong>Technologies:</strong> ${project.technologies}</p>
                        <div class="links">
                            ${project.github_link ? `<a href="${project.github_link}" target="_blank">GitHub</a>` : ''}
                            ${project.demo_link ? `<a href="${project.demo_link}" target="_blank">Demo</a>` : ''}
                        </div>
                    `;
                    container.appendChild(card);
                });
            })
            .catch(err => console.error('Error fetching projects:', err));
    </script>
</body>
</html>
