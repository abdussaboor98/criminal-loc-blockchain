function onlyNum(e){
    var unicode = e.charCode? e.charCode : e.keyCode;
    console.log(unicode);
    if (unicode!=8){
        if (unicode<48 || unicode>57)
            return false;
    }
}

function minSizeA(e){
    if(e.target.value.length < 12){
        $(e.target.labels[0]).show();
    }
    else{
        $(e.target.labels[0]).hide();
    }
}

function minSizeP(e){
    //console.log(e.target);
    if(e.target.value.length < 12){
        $(e.target.labels[0]).show();
    }
    else{
        $(e.target.labels[0]).hide();
    }
}

function isRequired(e){
    if(e.target.value.length == 0){
        $(e.target.labels[0]).show();
    }
    else{
        $(e.target.labels[0]).hide();
    } 
}

function onlyFirstAlpha(e){
    var length = e.target.value.length;
    var unicode = e.charCode? e.charCode : e.keyCode;
    if(length  == 0){
        console.log(unicode);
        if (unicode<65 || unicode>90)
            return false;
    }
    else{
        if (unicode!=8){
            if (unicode<48 || unicode>57)
                return false;
        }
    }
}

function checkRequiredFields2(field1,field2){
    if($(field1).val().length == 0)
        $($(field1)[0].labels[0]).show();
    if($(field2).val().length == 0)
        $($(field2)[0].labels[0]).show();
    else 
        return true;
}
