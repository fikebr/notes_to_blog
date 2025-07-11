# gi.cmd a windows batch script to get a default .gitignore file from Toptal

```
@echo off


echo.
echo ### GITIGNORE from Toptal ###
echo.
echo checking... https://www.toptal.com/developers/gitignore/api/%*
echo creating the .gitignore file
echo.

curl.exe https://www.toptal.com/developers/gitignore/api/%* > .gitignore
```

1. Place this batch file somewhere in the PATH
2. In your project folder run ```gi python```
	1. where "python" is the type of ignore file that you want
