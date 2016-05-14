// Eloquent JS given functions
function average(array) {
  function plus(a, b) { return a + b; }
  return array.reduce(plus) / array.length;
}

var byName = {};
ancestry.forEach(function(person) {
  byName[person.name] = person;
});

/* Looks through dictionary and returns average age between birth-year of each person
and birth-year of their mother */
function averageAge(dict){
  var ageArray = [];
  // copy dict in function argument into local var called 'byName'
  // since we will be deleting entries, I dont want to modify exisiting dict
  var byName = dict;
  for (name in byName){
    // if entry doesn't have a mother delete from dict
    if(!byName[name]['mother']){
      delete byName[name];
      // found this little gem that goes back to top of for loop without
      // executing code below
      continue;
    }
    var mother = byName[name]['mother'];
    //if mother not in dict, delete person from dict (can't compare ages)
    if (!byName[mother]){
      delete byName[name];
      continue;
    }

    // if element passes the two tests above, execute the average age code
    var ageDiff = byName[name]['born'] - byName[mother]['born'];
    ageArray.push(ageDiff);

  }
  console.log(ageArray);
  return average(ageArray);
}

console.log(averageAge(byName));
