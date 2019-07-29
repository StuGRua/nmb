function kookie_update(){
    var b = document.getElementById("kookie_main");
    b.innerText = "WAITING`";
    $.ajax({url:"/kookie",
            type:"UPDATE",
            async:true,
            success:function(result){
                console.log(parseInt(result)+'change kookie OK!');
                if(parseInt(result)==1){
                kookie_get();
                }
                else{  
                    alert(result);
                }
            }
        })
    
}
function kookie_get(){
    $.ajax({
        url:"/kookie",
        type:"GET", 
        success:function(result){
            var a =document.getElementById("kookie_main");
            a.innerHTML = '饼干：'+result;
            }
        }
    )
}