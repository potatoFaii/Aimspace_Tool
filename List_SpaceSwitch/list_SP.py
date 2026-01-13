=====================
   _GimbalLoc_fix
=====================
// INSTRUCTION
-drag and drop ,filePath provided
_______________________________________________________________________________
    _____________
   _\__FUNCTION__\_
_______________________________________________________________________________
-MUST select a controller and function the script ,the outliner will appear A locator of your selection naming plus axis ,for gimbal cheat use
-one selection 
-the locator naming will according to your selection ctrl naming and rename it ,to avoid if theres same naming appear , also if the locator already exist the
script will warning already exist , to get a new one u must bake the ctrl animation again then delete the exists locator ,then function the script again
-after finish animation animator just hav to bake the ctrl ,and manual delete the locator that created
-for extra function below is to grab the locator (can be more than one) ,GRAB those locator and store inside the textFieldGrp ,then click Bake Animation
-the button will be automatic detect back the source of the controller ,bake the timeline then remove the locator to cleanup
-beware that only locator that created from this script can be work 
-modify date 8/16/2022 , 9/15/2022
_______________________________________________________________________________
     _________
    _\__LOGS__\_
_______________________________________________________________________________
_for rigger plan notes and purpose *can ignore
_#future wise planning note

\ create a column that can store the locator(target) and control(main) ,so that when animator finish the animation then it can straight detect the ctrl and bake it 
\ modify the warning to make it instead of warning the locator with rotation order ,it will warning the locator naming(fullpath) , also select the locator that exist
\ euler filter working on
-modified date 8/19/2022

\ UI updated to fit the condition
\ hmmm probably setup a manual tab? for the locator to match the position ,select target and main the apply the step 
-modified date 8/21/2022

\ complete the source grab function (able to grab more than one locator ,store and bake animation ,remove the target
\ havent complete yet (warning also choose selection,manual tab ,and UI redesign based on shengchuan request more organise)
-modified date 9/15/2022

\ reupdate UI to easier feature 
\ create manual so animator can set it freely 
\ remodify so can be multi selection instead of one selection
-modified date 3/6/2023

\ update DOUBLE side and some naming , double create two locator with the function similar to single
\ option side and targetBake side ,option is create so that future wise maybe can make it to diff size ,color or more feature plan
\ UI side change slightly 
\ modify can be discuss with animator after feature use smtg
-modified date 4/14/2023

\ update LIST for the bake animation ctrls (listing for animator so can track back the ctrl after bake animation happen)
\ assign OPTIONS as extra function ,so that before build locator can assign primary color to the locator that it wont cause confusion which locator is create by the script
-modified 4/19/2023

\   _________________
\  _\__MAJOR UPDATE__\_
\ maya button ui annot fixed
\ all error fixed , moving back to correct loop and some minor naming
\ added loading bar for each button ,to avoid huge animation bake loading freeze
\ added cmds.refresh(suspend=True), bake animation faster
\ mel.eval print each button function ,at below
\ remove animLayer attribute from animLayer ,if animLayer is empty then remove it automatic
\ manual locator added center pivot feature ,more convinience than OAT
\ bake animation using connectioneditor instead ,more consistance than naming ,every locator now enable to bake source easier
\ rigger credit added , futurewise make it more detail 
-modified 3/18/2024

\ resize the icon
\ added popupmenuItem ,still abit buggy 
\ debug some script minor issue
-modified  8/27/2024

\ resize the icon
\ added popupmenuItem ,still abit buggy 
\ debug some script minor issue
-modified  8/27/2024

\\ UI \\
\ optional setup for single,double and manual
\ modify tab move to above using checkbox to tick/untick if animator want to modify controller from the aspect 
\ key setting
\ remove grab and instant select controller for bake animation
\ refer latest script for framelayout collapse , good for windowUI tidy purpose
\ preset customise (type,color,outliner,size,preset save,display annotation,keyframe bake range)
\ able to access to different maya version without any bug 
\\ Function \\ 
\ bake animation include clean animLayer excess unused
\ better organized naming 
\ include undoInfo and refresh (faster bake and able undo if anything happen)
\ progressWindow allow animator to know the script is functioning without freeze or crash
\ RND
-modified 1/6/2026