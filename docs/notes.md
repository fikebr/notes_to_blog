# notes to blog post app

an application that uses python and crewai to take my unoganized notes on a topic and fleshes them out with some extra research, organizes the notes, writes a well formated blog file & generates some supplemental images.

## requirements

- use crewai for all of the agentic integration with LLMs and process flow management.
- use openrouter for the LLM interface
- use replicate.com for the text-to-image work
- the output will be a well structured markdown *.md file with a frontmatter header
- use the brave browser api for and web searching

## process flow

1) check the inbox folder for a new notes file.
2) summarize my notes
3) get a title and description for the blog post
4) write an intro and conclusion to the post
5) decide on 2-5 subheadings for the post
6) research the content for the subheadings
7) write the subheadings
8) make a prompt for the header image and any supplemental images
9) generate those images
10) link to those images in the blog post
11) pick a category from the available list of categories (stored in a config file)
12) pick 2-5 tags for the post
13) write the frontmatter header for the post (use a sample frontmatter that is stored in a templates folder)
14) pick a filename
15) write the file and save the images to the target location (stored in config)

## frontmatter

+++
title = "Transferring Files from VirtualBox Guest to Host with VBoxManage"
description = "Using VBoxManage guestcontrol to copy files from a Linux VM to Windows host without shared folders"
date = 2025-05-29
draft = true

[taxonomies]
categories=["virtualization"]
tags=["virtualbox", "linux", "windows", "command-line", "vm"]
+++

## Categories

- development
- computer
- home
- ai
- business
- crafting
- health
- diy
- recipes
