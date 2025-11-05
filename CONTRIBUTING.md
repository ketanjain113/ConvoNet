# Contributing to ConvoNet

Thank you for your interest in contributing to ConvoNet! This guide will help you understand how to add new files and contribute to this project.

## How to Push New Files

### Prerequisites
- Git installed on your machine
- A GitHub account
- Basic knowledge of Git commands

### Step 1: Fork the Repository
1. Go to [https://github.com/ketanjain113/ConvoNet](https://github.com/ketanjain113/ConvoNet)
2. Click the "Fork" button in the top right corner
3. This creates a copy of the repository in your GitHub account

### Step 2: Clone Your Fork
Replace `<your-username>` with your actual GitHub username:
```bash
git clone https://github.com/<your-username>/ConvoNet.git
cd ConvoNet
```

### Step 3: Create a New Branch
Always create a new branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

### Step 4: Add Your New Files
1. Add your new files to the appropriate directory in the project
2. For Django-related files:
   - Models, views, templates go in the `chatroom/` directory
   - Static files (CSS, JS) should be in appropriate static directories
   - Templates go in the `templates/` directory

### Step 5: Stage Your Files
Add your new files to Git:
```bash
# Add specific files
git add path/to/your/file.py

# Or add all new files
git add .
```

### Step 6: Commit Your Changes
Write a clear commit message describing what you've added:
```bash
git commit -m "Add feature: brief description of what you added"
```

### Step 7: Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### Step 8: Create a Pull Request
1. Go to your fork on GitHub
2. Click "Pull Request" button
3. Select your branch and click "Create Pull Request"
4. Add a clear title and description of your changes
5. Submit the pull request

## Project Structure

This is a Django-based chat application. Here's the structure:

```
ConvoNet/
├── chatroom/           # Main Django project directory
│   ├── chat/          # Chat application
│   ├── chatroom/      # Project settings
│   ├── templates/     # HTML templates
│   └── media/         # User-uploaded media files
└── README.md          # Project documentation
```

## Guidelines for Contributions

### Code Quality
- Follow PEP 8 style guide for Python code
- Write clear, descriptive variable and function names
- Add comments for complex logic

### Before Submitting
- Test your changes locally
- Make sure your code doesn't break existing functionality
- Update documentation if needed

### What to Contribute
- Bug fixes
- New features
- Documentation improvements
- UI/UX enhancements
- Performance improvements

## Getting Help

If you have questions or need help:
1. Check existing issues on GitHub
2. Create a new issue describing your question
3. Be patient and respectful in all communications

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help create a positive community

Thank you for contributing to ConvoNet! 🚀
