+++
title = "{{ title }}"
description = "{{ description }}"
date = {{ date }}
draft = {{ draft }}

[taxonomies]
categories = ["{{ categories | join('", "') }}"]
tags = ["{{ tags | join('", "') }}"]
+++

# {{ title }}

{{ introduction }}

{% for subheading in subheadings %}
## {{ subheading.title }}

{{ subheading.content }}

{% if subheading.image %}
![{{ subheading.image.alt_text }}]({{ subheading.image.filename }})
{% endif %}

{% endfor %}

{{ conclusion }} 