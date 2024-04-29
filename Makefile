build:
	docker build -t cr.yandex/crphs06dffie5ov65du4/norma:$(shell git rev-parse --short HEAD) -f Dockerfile .

push:
	docker push cr.yandex/crphs06dffie5ov65du4/norma:$(shell git rev-parse --short HEAD)
