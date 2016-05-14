function processData(input) {
    input=input.split('\n');
    for(var i=1;i<parseInt(input[0]);i++){
        var even = '';
        var odd = '';
        var string = input[i]
        for(var j=0;j<string.length;j++){
            if (j % 2 == 0){
                even += string[j];
            } else {
                odd += string[j]
            }
        }
       console.log(even, odd);
    }
}

string = '2\nHacker Rank\n yoyo'
processData(string)
