# yandex-fotki-to-flickr
Migrate photos with metadata from Yandex.Fotki to Flickr

Russian
-------

Фотохостинг Яндекс.Фотки предательски закрывается, оставляя тысячи пользователей без привычной возможности публиковать фотографии и обсуждать их, а также всех без картинок в огромном количестве блогов. Я размещаю инструменты, которые использовал сам для переноса своей коллекции фотографий с Яндекс.Фоток на Flickr с сохранением альбомов, названий фотографий, описаний, меток и геграфической привязки и с записью ссылок на фотографии на Flickr для автоматического поиска-замены в публикациях.

Требования
------------
1. Желание перенести фотографии с Яндекс.Фоток на Flickr.
2. Готовность к некоторой ручной работе.
3. Базовые знания Linux и Python.

Инструкция
------------
1. Сгенерировать код для вставки альбомов на Яндекс.Фотках по этой инструкции. http://oleksite.com/kak-skachat-ves-albom-iz-yandeks-fotok/ В кратце, сгенерировать HTML-код для всех альбомов по кнопке «Получить код» на странице альбома и сохранить его в файлы с именами `Album 01.txt`, `Album 02.txt` и т. д.

2. Получить список всех альбомов и фотографий с метаданными. Скрипт загрузит и разберёт страницы фотографий и получит из них необходимую информацию. Конечно, для таких целей нужно использовать API, но Яндекс не имеет нчего против page scraping.

```./listAlbums.py```

Будут созданы два .csv-файла.

* `Albums.csv` содержит список альбомов в следующем формате.

```index;album_name;picture_count;album_link;filename```

* `Pictures.csv` содержит список фотографий в следующем формате.

```page_link;name;description;tags;small_image_link;orig_image_link;latitude;longitude;album_name```
  
3. Задать путь для загрузки файлов в переменных `path_small` и `path_orig` в `downloadPictures.py` и начать загружать фотографии. Процесс может быть остановлен, при перезапуске он продолжится с первой незагруженной фотографии.

```./downloadPictures.py```
  
4. Задать путь к загруженным файлам в переменной `path_orig` в `setGpsToExif.py` и начать запись координат в EXIF оригинальных файлов, для которых координаты есть в .csv-файлй, но их нет в EXIF (то есть, только для тех фотографий, которые были привязаны к карте через интерфейс Яндекс.Фоток). Запуск exiftool занимает много времени. Проверить результат можно при помощи https://www.pic2map.com/.

```sudo apt-get install exiftool
./setGpsToExif.py
```
  
5. Зарегистрироваться на Flickr, получить ключ API. Создать текстовый файл `api_key.txt` в котором задать API key, API secret и User ID (в формате 123456789@N00) с разделителем в виде перевода строки.

6. Установить Python Flickr API.
```wget https://pypi.python.org/packages/b1/f1/d10fa0872e4f781c2ed47e94e728ecd3c1998f8c8d12e78c7329a25d0727/flickrapi-2.4.0.tar.gz#md5=94e9b9ac81b1dae1b226e22ac6a4375b
tar -xvf flickrapi-2.4.0.tar.gz
cd flickrapi-2.4.0/
sudo apt-get install python3-setuptools
sudo python3 setup.py install
```

7. Задать путь к загруженным файлам в переменной `path_orig` в `create_albums.py` и начать загрузку фотографий и создание альбомов. при первом запуске потребуется выполнить авторизацию ключа API для загрузки фотографий в выбранный аккаунт Flickr. Нужно перезапускать скрипт, пока все фотографии не будут загружены.

```./create_albums.py```

Я старался создать красивый последовательный алгоритм, который загружает фотографии, создаёт альбомы, добавляет фотографии в альбомы и получает ссылки на фотографии, но периодические зависания на открытии и закрытии соединения заставили отказаться от него в пользу просто загрузки по 50 фотографий за раз, оставля возможность удалить вручную фотографии в случае неудачной загрузки. Скрипт отображает диалог в случае ошибок. Вы можете менять алгоритм на свой вкус.

В результате .csv-файлы будут обновлены.

* в `Albums.csv` добавятся ID альбома и ссылка на альбом на Flickr.

```index;album_name;picture_count;album_link;filename;flickr_album_id;flickr_album_link```

* D `Pictures.csv` добавится код для вставки изображения для Flickr.

```page_link;name;description;tags;small_image_link;orig_image_link;latitude;longitude;album_name;flickr_embed_code```

Автор программы Alexander Yampolsky.

Вопросы присылайте по адресу yampa@yandex.ru.

English
-------

Yandex.Fotki photo hosting service that is traitorously closing, leaving thousands of users without accustomed way of sharing and discussing their photographies, and everyone without pictures in a lot of blogs. I'm sharing tools I've used myself to migrate my picture collection from Yandex.Fotki to Flickr while preserving albums, photo names, descriptions, tags and geolocation, and saving links to pictures on Flickr for automatic find-replace in publications.

Requirements
------------
1. Eagerness to transfer pictures from Yandex.Fotki to Flickr.
2. Readiness for some manual work.
3. Basic Linux and Python knowledge.

Instructions
------------
1. Generate code for all albums using this instructions. http://oleksite.com/kak-skachat-ves-albom-iz-yandeks-fotok/ In short, generate HTML-code for all albums with "Получить код" ("Get code") button on the album page and save it to files with names `Album 01.txt`, `Album 02.txt` and so on.

2. Get list of albums and list of photos with metadata. The script will download and parse pages for all pictures, extracting required information. Of course, such thing should be done with API, but Yandex doesn't frown upon page scraping.

```./listAlbums.py```

Two .csv files will be created.

* `Albums.csv` contains list of albums in the following format.

```index;album_name;picture_count;album_link;filename```

* `Pictures.csv` contains list of pictures in the following format.

```page_link;name;description;tags;small_image_link;orig_image_link;latitude;longitude;album_name```
  
3. Set download location in `path_small` and `path_orig` variables in `downloadPictures.py` and start downloading pictures. The process may be interrupted, it will continue on restart of script.

```./downloadPictures.py```
  
4. Set download location in `path_orig` variable in `setGpsToExif.py` and start writing GPS to EXIF of original files, where geolocation information exists in .csv file and doesn't exist EXIF (so, only for pictures that were placed on map using Yandex.Fotki interface). Running exiftool takes much time. The result can be verified with https://www.pic2map.com/.

```sudo apt-get install exiftool
./setGpsToExif.py
```
  
5. Register on Flickr, get API key. Create text file `api_key.txt` with API key, API secret and User ID (in 123456789@N00 format) delimited with newline character.

6. Install Python Flickr API.
```wget https://pypi.python.org/packages/b1/f1/d10fa0872e4f781c2ed47e94e728ecd3c1998f8c8d12e78c7329a25d0727/flickrapi-2.4.0.tar.gz#md5=94e9b9ac81b1dae1b226e22ac6a4375b
tar -xvf flickrapi-2.4.0.tar.gz
cd flickrapi-2.4.0/
sudo apt-get install python3-setuptools
sudo python3 setup.py install
```

7. Set download location in `path_orig` variable in `create_albums.py` and start uploading pictures and creating albums. On the first run authorization of API key for uploading pictures in given Flickr account will be required. The script should be restarted until all the pictures are uploaded.

```./create_albums.py```

A nice straightforward algorithm was designed to upload pictures, create albums, assign pictures to albums and get links for every picture, but periodic getting stuck on opening and closing connection made me decide to just upload 50 pictures at a time, leaving ability to delete incorrectly uploaded pictures manually. The script will display prompt on errors. You can edit the algorithm to your taste.

The .csv files will be updated.

* In `Albums.csv` album ID and a link to album on Flickr will be added.

```index;album_name;picture_count;album_link;filename;flickr_album_id;flickr_album_link```

* In `Pictures.csv` picture embed code on Flicke will be added.

```page_link;name;description;tags;small_image_link;orig_image_link;latitude;longitude;album_name;flickr_embed_code```

Author of this program is Alexander Yampolsky.

For questions, please contact yampa@yandex.ru.
