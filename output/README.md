# Output Directory

This directory contains the generated blog posts from processed notes.

## Structure

Each blog post is saved as a markdown file with the following structure:

```
+++
title = "Blog Post Title"
description = "Post description"
date = YYYY-MM-DD
draft = true

[taxonomies]
categories = ["category"]
tags = ["tag1", "tag2", "tag3"]
+++

# Blog Post Content

[Formatted content with images and structure]
```

## File Organization

- Blog posts are saved with descriptive filenames
- Each post includes proper frontmatter metadata
- Images are referenced and stored in the `images/` directory
- Posts are ready for publishing to static site generators

## Usage

The generated blog posts can be:

1. **Published directly** to platforms like:
   - Hugo static site generator
   - Jekyll
   - Gatsby
   - Other markdown-compatible platforms

2. **Further edited** manually if needed

3. **Customized** with additional formatting or metadata

## Metadata

Each blog post includes:
- Title and description
- Publication date
- Categories and tags
- Draft status
- Proper markdown formatting 