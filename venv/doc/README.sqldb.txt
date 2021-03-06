# DISMISSION NOTICE

The data used by the "sql" access system is no longer updated.
In the future, we'll support the new data from http://www.imdb.com/interfaces/


# REQUIREMENTS

You need SQLAlchemy.

SQLAlchemy home page: http://www.sqlalchemy.org/


[OTHER REQUIRED MODULES]
Obviously SQLAlchemy can access databases only through other
specific modules/packages, that you need to have installed (e.g.:
'mysql-python' for MySQL, 'psycopg' for PostgreSQL, and so on).


# SQL DATABASE INSTALLATION

Select a mirror of the "The Plain Text Data Files" from
the http://www.imdb.com/interfaces/ page and download
every file in the main directory (beware that the "diffs"
subdirectory contains _a lot_ of files you _don't_ need,
so don't start mirroring everything!).

Starting from release 2.4, you can just download the files you need,
instead of every single file; the files not downloaded will be skipped.
This feature is still quite untested, so please report any bug.

Create a database named "imdb" (or whatever you like),
using the tool provided by your database; as an example, for MySQL
you will use the 'mysqladmin' command:
  # mysqladmin -p create imdb
For PostgreSQL, you have to use the "createdb" command:
  # createdb -W imdb

To create the tables and to populate the database, you must run
the imdbpy2sql.py script:
  # imdbpy2sql.py -d /dir/with/plainTextDataFiles/ -u 'URI'

Where the 'URI' argument is a string representing the connection
to your database, with the schema:
  scheme://[user[:password]@]host[:port]/database[?parameters]

Where 'scheme' is one in "sqlite", "mysql", "postgres", "firebird",
"interbase", "maxdb", "sapdb", "mssql", "sybase", "ibm_db_sa".

Some examples:
    mysql://user:password@host/database
    postgres://user:password@host/database
    mysql://host/database?debug=1
    postgres:///full/path/to/socket/database
    postgres://host:5432/database
    sqlite:///full/path/to/database
    sqlite:/C|/full/path/to/database
    sqlite:/:memory:

For other information you can read the SQLAlchemy documentation.


# TIMING

The performances are hugely dependant upon the underlying Python
module/package used to access the database.  The imdbpy2sql.py script
has a number of command line arguments, useful to chose amongst
presets that can improve performances, using specific database servers.

The fastest database appears to be MySQL, with about 200 minutes to
complete on my test system (read below).
A lot of memory (RAM or swap space) is required, in the range of
at least 250/500 megabytes (plus more for the database server).
In the end, the database will require between 2.5GB and 5GB of disc space.

As said, the performances varies greatly using a database server or another:
MySQL, for instance, has an executemany() method of the cursor object
that accept multiple data insertion with a single SQL statement; other
database requires a call to the execute() method for every single row
of data, and they will be much slower - from 2 to 7 times slower than
MySQL.

There are generic suggestions that can lead to better performances,
like turning off your filesystem journaling (so it can be a good idea to
remount an ext3 filesystem as ext2).  Another option is the use of a
ramdisk/tmpfs, if you have enough RAM.  Obviously these have effect only
at insert-time: during the day-to-day use, you can turn your journaling
on again.  You can also consider the use of the CSV output, explained
below (but be sure that your database server of choice is able to
import CSV files).

I've done some tests, using an AMD Athlon 1800+, 1GB of RAM, over a
complete plain text data files set (as of 11 Apr 2008, with more than
1.200.000 titles and over 2.200.000 names):

      database         |  time in minutes: total (insert data/create indexes)
 ----------------------+-----------------------------------------------------
   MySQL 5.0 MyISAM    |  205 (160/45)
   MySQL 5.0 InnoDB    |  _untested_, see NOTES below.
   PostgreSQL 8.1      |  560 (530/30)
   SQLite 3.3          |  ??? (150/???) - very slow building indexes.
                       |  Timed with the "--sqlite-transactions" command
                       |  line option; otherwise it's _really_ slow: even
                       |  35 hours or more.
   SQLite 3.7          |  65/13 - with --sqlite-transactions and using a SSD hard disk
   SQL Server          |  about 3 or 4 hours.

If you have different experiences, please tell me!
As expected, the most important things that you can do to improve performances are:
1. use an in-memory filesystem or an SSD disk.
2. use the -c /path/to/empty/dir argument to use CSV files.
3. follow the specific notes about your database server.


# NOTES

[save the output]
The imdbpy2sql.py will print a lot of debug information on standard output;
you can save it in a file, appending (without quotes) "2>&1 | tee output.txt"


[Microsoft Windows paths]
It's much safer, in a Microsoft Windows environment, to use full paths
for the values of the '-c' and '-d' arguments, complete with drive letter.
The best thing is to use _UNIX_ path separator, and to add a leading
separator.  E.g.:
  -d C:/path/to/imdb_files/ -c C:/path/to/csv_tmp_files/


[MySQL]
In general, if you get an embarrassingly high numbero of "TOO MANY DATA
... SPLITTING" lines, consider increasing max_allowed_packet (in the
configuration of your MySQL server) to at least 8M or 16M.
Otherwise, inserting the data will be very slow, and some data may
be lost.


[MySQL InnoDB and MyISAM]
InnoDB is abysmal slow for our purposes: my suggestion is to always
use MyISAM tables and - if you really want to use InnoDB - convert
the tables later.
The imdbpy2sql.py script provides a simple way to manage these cases,
see ADVANCED FEATURES below.

In my opinion, the cleaner thing to do is to set the server to use
MyISAM tables or - you you can't modifiy the server - use the
--mysql-force-myisam command line option of imdbpy2sql.py.
Anyway, if you really need to use InnoDB, in the server-side settings
I recommend to set innodb_file_per_table to "true".

Beware that the conversion will be extremely slow (some hours), but
still faster than using InnoDB from the begin.
You can use the "--mysql-innodb" command line option to force the
creation of a datbase with MyISAM tables, converted at the end
into InnoDB.


[Microsoft SQL Server/SQLExpress]
If you get and error about how wrong and against nature is the
blasphemous act of inserting indentity keys, you can try to fix it
with the new custom queries support; see ADVANCED FEATURES below.

As a shortcut, you can use the "--ms-sqlserver" command line option
to set all the needed options.


[SQLite speed-up]
For some reason, SQLite is really slow, except when used with
transactions; you can use the '--sqlite-transactions' command
line option to obtain acceptable performances.
The same command, also turns off "PRAGMA synchronous".

SQLite seems to hugely benefit from the use of a non-journaling
filesystem and/or of a ramdisk/tmpfs: see the generic suggestions
discussed above in the TIMING section.


[SQLite failure]
It seems that, with older versions of the python-sqlite package, the first
run may fail; if you get a DatabaseError exception saying "no such table",
try running again the command with the same arguments.  Double funny, uh? ;-)


[data truncated]
If you get an insane amount (hundreds or thousands, on various text
columns) of warnings like these lines:

  imdbpy2sql.py:727: Warning: Data truncated for column 'person_role' at row 4979
  CURS.executemany(self.sqlString, self.converter(self.values()))

you probably have a problem with the configuration of your database.
The error came from strings that get cut at the first non-ASCII char (and
so you're losing a lot of information).
To obviate at this problem, you must be sure that your database
server is set up properly, with the use library/client configured
to communicate with the server in a consistent way.
E.g., for MySQL you can set:
  character-set-server   = utf8
  default-collation      = utf8_unicode_ci
  default-character-set  = utf8

of even:
  character-set-server   = latin1
  default-collation      = latin1_bin
  default-character-set  = latin1


[adult titles]
Beware that, while running, the imdbpy2sql.py script will output a lot
of strings containing both person names and movie titles.  The script
has absolutely no way to know that the processed title is an adult-only
movie, so... if you leave it running and your little daughter runs to you
screaming 'daddy!  daddy!  what kind of animals Rocco trains in the
documentary "Rocco: Animal Trainer 17"???'... well it's not my fault! ;-)


# SQL USAGE

Now you can use IMDbPY with the database:
  from imdb import IMDb
  i = IMDb('sql', uri='YOUR_URI_STRING')
  resList = i.search_movie('the incredibles')
  for x in resList: print(x)
  ti = resList[0]
  i.update(ti)
  print(ti['director'][0])

and so on...


# ADVANCED FEATURES

With the -e (or --execute) command line argument you can specify
custom queries to be executed at certain times, with the syntax:
  -e "TIME:[OPTIONAL_MODIFIER:]QUERY"

Where TIME is actually one of these: 'BEGIN', 'BEFORE_DROP', 'BEFORE_CREATE',
'AFTER_CREATE', 'BEFORE_MOVIES', 'BEFORE_CAST', 'BEFORE_RESTORE',
'BEFORE_INDEXES' and 'END'.

The only available OPTIONAL_MODIFIER is 'FOR_EVERY_TABLE' and it
means that the QUERY command will be executed for every table in the
database (so it doesn't make much sense to use it with BEGIN, BEFORE_DROP
or BEFORE_CREATE time...), replacing the "%(table)s" text in the QUERY
with the appropriate table name.

Other available TIMEs are: 'BEFORE_MOVIES_TODB', 'AFTER_MOVIES_TODB',
'BEFORE_PERSONS_TODB', 'AFTER_PERSONS_TODB', 'BEFORE_CHARACTERS_TODB',
'AFTER_CHARACTERS_TODB', 'BEFORE_SQLDATA_TODB', 'AFTER_SQLDATA_TODB',
'BEFORE_AKAMOVIES_TODB' and 'AFTER_AKAMOVIES_TODB'; they take no modifiers.
Special TIMEs 'BEFORE_EVERY_TODB' and 'AFTER_EVERY_TODB' apply to
every BEFORE_* and AFTER_* TIME above mentioned.
These commands are executed before and after every _toDB() call in
their respective objects (CACHE_MID, CACHE_PID and SQLData instances);
the  "%(table)s" text in the QUERY is replaced as above.

You can specify so many -e arguments as you need, even if they
refers to the same TIME: they will be executed from the first to the last.
Also, always remember to correctly escape queries: after all you're
passing it on the command line!

E.g. (ok, quite a silly example...):
  -e "AFTER_CREATE:SELECT * FROM title;"

The most useful case is when you want to convert the tables of a MySQL
from MyISAM to InnoDB:
  -e "END:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=InnoDB;"

If your system uses InnoDB by default, you can trick it with:
  -e "AFTER_CREATE:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=MyISAM;" -e "END:FOR_EVERY_TABLE:ALTER TABLE %(table)s ENGINE=InnoDB;"

You can use the "--mysql-innodb" command line option as a shortcut
of the above command.

Cool, uh?

Another possible use is to fix a problem with Microsoft SQLServer/SQLExpress:
to prevent errors setting IDENTITY fields, you can run something like this:
  -e 'BEFORE_EVERY_TODB:SET IDENTITY_INSERT %(table)s ON' -e 'AFTER_EVERY_TODB:SET IDENTITY_INSERT %(table)s OFF'

You can use the "--ms-sqlserver" command line option as a shortcut
of the above command.

To use transactions to speed-up SQLite, try:
  -e 'BEFORE_EVERY_TODB:BEGIN TRANSACTION;' -e 'AFTER_EVERY_TODB:COMMIT;'

Which is also the same thing the command line option '--sqlite-transactions'
does.


# CSV files

Keep in mind that actually only MySQL, PostgreSQL and IBM DB2 are
supported.  Moreover, you may incur in problems (e.g.: your
postgres _server_ process must have reading access to the directory
you're storing the CSV files).

To create (and import) a set of CSV files, run imdbpy2sql.py with the
syntax:
  ./imdbpy2sql.py -d /dir/with/plainTextDataFiles/ -u URI -c /directory/where/to/store/CSVfiles

The created files will be imported near the end of the imdbpy2sql.py
processing; notice that after that, you can safely cancel these files.


# CSV partial processing

It's possible, since IMDbPY 4.5, to separate the two steps involved using
CSV files.
With the --csv-only-write command line option the old database will
be zeroed and the CSV files saved (along with imdbIDs information).
Using the --csv-only-load option you can load these saved files into
an existing database (this database MUST be the one left almost empty
by the previous run).
Beware that right now the whole procedure is not very well tested.
Using both commands, on the command line you still have to specify
the whole "-u URI -d /path/plainTextDataFiles/ -c /path/CSVfiles/"
series of arguments.


