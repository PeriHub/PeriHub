export const deepCopy = function (obj) {
  var rv;

  switch (typeof obj) {
    case "object":
      if (obj === null) {
        // null => null
        rv = null;
      } else {
        switch (toString.call(obj)) {
          case "[object Array]":
            // It's an array, create a new array with
            // deep copies of the entries
            rv = obj.map(deepCopy);
            break;
          case "[object Date]":
            // Clone the date
            rv = new Date(obj);
            break;
          case "[object RegExp]":
            // Clone the RegExp
            rv = new RegExp(obj);
            break;
          // ...probably a few others
          default:
            // Some other kind of object, deep-copy its
            // properties into a new object
            rv = Object.keys(obj).reduce(function (prev, key) {
              prev[key] = deepCopy(obj[key]);
              return prev;
            }, {});
            break;
        }
      }
      break;
    default:
      // It's a primitive, copy via assignment
      rv = obj;
      break;
  }
  return rv;
};

export function parseFromJson(obj, input) {
  for (var i = 0; i < Object.keys(input).length; i++) {
    var paramName = Object.keys(input)[i];
    // console.log(this[paramName]);
    // console.log(input[paramName]);

    // this[paramName] = [...input[paramName]];
    if (Array.isArray(input[paramName])) {
      if (obj[paramName].length > input[paramName].length) {
        for (var j = obj[paramName].length; j >= input[paramName].length; j--) {
          obj[paramName].splice(j, 1);
        }
      }
      if (obj[paramName].length < input[paramName].length) {
        for (var j = obj[paramName].length; j < input[paramName].length; j++) {
          obj[paramName].push({});
        }
      }
      obj[paramName] = [...input[paramName]];
    } else {
      obj[paramName] = { ...input[paramName] };
    }
  }
}
