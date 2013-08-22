function Map(storageId) {
    this.current = undefined;
    this.size = 0;
    this.storageId = storageId;
    if (this.storageId) {
        this.keys = new Array();
        this.disableLinking();
    }
}

Map.noop = function() {
    return this;
};

Map.illegal = function() {
    throw new Error("illegal operation for maps without linking");
};

// map initialisation from existing object
// doesn't add inherited properties if not explicitly instructed to:
// omitting foreignKeys means foreignKeys === undefined, i.e. == false
// --> inherited properties won't be added
Map.from = function(obj, foreignKeys) {
    var map = new Map;
    for(var prop in obj) {
        if(foreignKeys || obj.hasOwnProperty(prop))
            map.put(prop, obj[prop]);
    }
    return map;
};

Map.prototype.disableLinking = function() {
    this.link = Map.noop;
    this.unlink = Map.noop;
    this.disableLinking = Map.noop;

    this.next = Map.illegal;
    this.key = Map.illegal;
    this.value = Map.illegal;
//    this.removeAll = Map.illegal;


    return this;
};

// overwrite in Map instance if necessary
Map.prototype.hash = function(value) {
    return (typeof value) + ' ' + (value instanceof Object ?
        (value.__hash || (value.__hash = ++arguments.callee.current)) :
        value.toString());
};

Map.prototype.hash.current = 0;

// --- mapping functions

Map.prototype.get = function(key) {
    var item = this[this.hash(key)];
    if (item === undefined) {
        if (this.storageId) {
            try {
                var itemStr = localStorage.getItem(this.storageId + key);
                if (itemStr && itemStr !== 'undefined') {
                    item = JSON.parse(itemStr);
                    this[this.hash(key)] = item;
                    this.keys.push(key);
                    ++this.size;
                }
            } catch (e) {
                printObject(e);
            }
        }
    }
    return item === undefined ? undefined : item.value;
};

Map.prototype.put = function(key, value) {
    var hash = this.hash(key);

    if(this[hash] === undefined) {
        var item = { key : key, value : value };
        this[hash] = item;

        this.link(item);
        ++this.size;
    }
    else this[hash].value = value;
    if (this.storageId) {
        this.keys.push(key);
        try {
            localStorage.setItem(this.storageId + key, JSON.stringify(this[hash]));
        } catch (e) {
            printObject(e);
        }
    }
    return this;
};

Map.prototype.remove = function(key) {
    var hash = this.hash(key);
    var item = this[hash];
    if(item !== undefined) {
        --this.size;
        this.unlink(item);

        delete this[hash];
    }
    if (this.storageId) {
        try {
            localStorage.setItem(this.storageId + key, undefined);
        } catch (e) {
            printObject(e);
        }
    }
    return this;
};

// only works if linked
Map.prototype.removeAll = function() {
    if (this.storageId) {
        for (var i=0; i<this.keys.length; i++) {
            this.remove(this.keys[i]);
        }
        this.keys.length = 0;
    } else {
        while(this.size)
            this.remove(this.key());
    }
    return this;
};

// --- linked list helper functions

Map.prototype.link = function(item) {
    if (this.storageId) {
        return;
    }
    if(this.size == 0) {
        item.prev = item;
        item.next = item;
        this.current = item;
    }
    else {
        item.prev = this.current.prev;
        item.prev.next = item;
        item.next = this.current;
        this.current.prev = item;
    }
};

Map.prototype.unlink = function(item) {
    if (this.storageId) {
        return;
    }
    if(this.size == 0)
        this.current = undefined;
    else {
        item.prev.next = item.next;
        item.next.prev = item.prev;
        if(item === this.current)
            this.current = item.next;
    }
};

// --- iterator functions - only work if map is linked

Map.prototype.next = function() {
    this.current = this.current.next;
};

Map.prototype.key = function() {
    if (this.storageId) {
        return undefined;
    } else {
        return this.current.key;
    }
};

Map.prototype.value = function() {
    if (this.storageId) {
        return undefined;
    }
    return this.current.value;
};