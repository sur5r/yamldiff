yamldiff
========

A semantic YAML diff utility.

````
yamldiff file1.yaml file2.yaml
````

will show recursively the values that are added removed or modified
from file1.yaml to file2.yaml.

The values of data type such as lists are compared by the whole value
(i.e.) must match exactly, but it is possible to refine the diff
output by
considering them unordered sets instead:

````
$ cat file1.yaml 
a_key : a value

a_list: 
    - {id: 1, val: uno}
    - {id: 2, val: dos}
    - {id: 3, val: tres}
$ cat file2.yaml 
a_key : another value

abother_key: some value
a_list: 
    - {id: 1, val: uno}
    - {id: 2, val: dos}
    - {id: 3, val: cuatro}
$ python yamldiff.py file1.yaml file2.yaml 
# Added keys:
+ abother_key: some value
# Modified keys:
a_key:
    - a value
    + another value
a_list:
    - [{id: 1, val: uno}, {id: 2, val: dos}, {id: 3, val: tres}]
    + [{id: 1, val: uno}, {id: 2, val: dos}, {id: 3, val: cuatro}]
$ python yamldiff.py file1.yaml file2.yaml --set-keys a_list
# Added keys:
+ abother_key: some value
# Modified keys:
a_key:
    - a value
    + another value
a_list:
    # Removed keys:
    - {id: 3, val: tres}
    # Added keys:
    + {id: 3, val: cuatro}
````

It is also possible to treat list as key value pairs, by specifying
the element of the list items to index on:

````
$ python yamldiff.py file1.yaml file2.yaml --set-keys a_list:id
# Added keys:
+ abother_key: some value
# Modified keys:
a_key:
    - a value
    + another value
a_list:
    # Modified keys:
    # Matching:
    {id: 3}
        # Modified keys:
        val:
            - tres
            + cuatro
````
