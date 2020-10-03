# pytalic2
An experimental calligraphic editor.  

Based on my previous "pytalic" project, but refactoring to take advantage of more Qt features and Pythonic constructs, as well as improving performance.  

Requires Python 3.x and PyQt5

Current screenshot of the editor:

![alt screenshot](https://github.com/dsizzle/pytalic2/blob/master/pytalic_editor_screen02.PNG)

My original vision was to create an editor for making calligraphic projects.  Most people use something like ProCreate these days, with a calligraphic pen, but I wanted an app dedicated to calligraphy with nice features for experimenting with different looks before taking brush to paper.  Probably not worth the effort, but I've learned a lot over the years working on it. 

In any case, I envisioned two apps, one being the 'font editor,' and the other being the 'project editor.'  The font editor is the code here.  I've never started the project editor. 

The font editor has a number of features:
- full undo support (a little buggy)
- adjustable font parameters and guides/gridlines that can be turned on and off
- nib sizes and character metrics overrideable per-character
- ability to save strokes as 'glyphs' and then instance them into other characters
- drag and drop of glyphs into scene
- a preview pane to visualize the entire font, and adjust kerning 
- snapping to the grid, to stroke points, the nib axes, and the grid axes
- constrained movement to x- and y- axes
- pixel-adjustable vertices and strokes
- ability to split strokes, or just add control points in the middle
- user color preferences
- cut/copy/paste

The project editor *would* have these features if I ever get to it:
- ability to load multiple character sets at once
- rotate and scale individual characters
- conform characters to a curve
- various layout tools, like aligning to axes and spacing words
- flourishing - connect strokes to the ends of other strokes for fancy curves
- multiple types of nibs: scroll, brush, italic, copperplate, etc.
- subtle stroke jitter for a less digital look
- per-character instance editing
- ability to export to images - maybe vector formats?

A piece of trivia: the reason the default ink color is red is because the first calligraphy pen my mom ever bought me as a kid was red, so it has a special place in my heart and mind. 

--
Icons are from http://www.fatcow.com/free-icons