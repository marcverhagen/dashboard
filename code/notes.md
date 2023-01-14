# Notes


```bash
$ docker run --name dashboard --rm -d
	-p 5000:5000
	-v /Users/Shared/data:/data
	-v /Users/Shared/archive:/archive
	dashboard
```


```bash
$ docker run --name dashboard --rm -d -p 5000:5000 -v $PWD/docs:/data/docs dashboard
$ docker run --rm -d -v /Users/Shared/data:/data -v /Users/Shared/archive/:/archive dashboard
```
