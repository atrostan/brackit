package com.example.d1

import android.content.pm.ActivityInfo
import android.os.Bundle
import androidx.core.view.GravityCompat
import androidx.appcompat.app.ActionBarDrawerToggle
import android.view.MenuItem
import androidx.drawerlayout.widget.DrawerLayout
import com.google.android.material.navigation.NavigationView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import android.view.View
import android.widget.*
import com.google.android.material.bottomnavigation.BottomNavigationView
import android.widget.Toast
import com.example.d1.dao.Tournament
import com.example.d1.dao.User
import org.json.JSONObject
import com.google.gson.Gson
import okhttp3.*
import org.json.JSONArray
import java.io.IOException

class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {
    val requestURL = "http://10.0.2.2:5000/api/"
    //val requestURL = "http://172.20.10.2:5000/api/"
    var client = OkHttpClient()
    private var LOG_IN = false
    var user: User? = null
    var jsonString = "nouser"
    var TournamentId = 0
    var Tournament_user_have = arrayListOf<Int>()
    var EDIT = false
    var TOKEN = ""
    var lossesList = arrayListOf<String>()
    var userList = arrayListOf<String>()
    var winsList = arrayListOf<String>()

    var tournamentsName = arrayListOf("Valentine's Day Lead-Off of the World Tournament",
        "By the Beach Labor Day 1st Down Tournament","Push the button again, I dare you.","Epic Last Day of School Back of the Net Tournament")

    var imageId = arrayListOf(R.drawable.tournament,R.drawable.tournament,R.drawable.tournament,R.drawable.tournament)
    private lateinit var list: ListView



        //when the bottom tab selected
    private lateinit var textMessage: TextView
    private val onNavigationItemSelectedListener = BottomNavigationView.OnNavigationItemSelectedListener { item ->
        when (item.itemId) {
            R.id.navigation_home -> {
               // textMessage.setText(R.string.title_home)
                return@OnNavigationItemSelectedListener true
            }
//            R.id.navigation_notifications -> {
//                textMessage.setText(R.string.title_profile)
//                return@OnNavigationItemSelectedListener true
//            }
        }
        false
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val toolbar: Toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)

        list = findViewById(R.id.list)

        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        //reset header
        resetHeader("Sign in","")

        //clear stats listview
        clearStatsAdapter()

        val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
        val navView: NavigationView = findViewById(R.id.nav_view)
        val toggle = ActionBarDrawerToggle(
            this, drawerLayout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawerLayout.addDrawerListener(toggle)
        toggle.syncState()

        navView.setNavigationItemSelectedListener(this)

        val bottomNavView: BottomNavigationView = findViewById(R.id.bottom_nav_view)

        textMessage = findViewById(R.id.message)
        bottomNavView.setOnNavigationItemSelectedListener(onNavigationItemSelectedListener)




        //after user login
        if (intent.hasExtra("user")){

            var gson = Gson()
            jsonString = intent.getStringExtra("user")
            println(jsonString+"----------")
            if (jsonString != "nouser"){
                LOG_IN = true
                user = gson.fromJson(jsonString,User::class.java)
                println(user)
                //set header with user name and email
                resetHeader(user!!.username,user!!.email)
                //set create tournament visible
                var menu = navView.menu
                var nav_cTournament = menu.findItem(R.id.nav_createTournament)
                var nav_history = menu.findItem(R.id.nav_history)
                var nav_logout = menu.findItem(R.id.nav_logout)
                var nav_stats = menu.findItem(R.id.nav_stats)
                var nav_edit_tournament = menu.findItem(R.id.nav_edit_tournament)
                nav_edit_tournament.setVisible(true)
                nav_cTournament.setVisible(true)
                nav_history.setVisible(true)
                nav_logout.setVisible(true)
                nav_stats.setVisible(true)
            }

        }

        if (intent.hasExtra("token")){
            TOKEN = intent.getStringExtra("token")
        }

        //update home page tournaments
        runOnUiThread {
            var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
            val list = findViewById<ListView>(R.id.list)
            listAdapter.notifyDataSetChanged()
            list.adapter = listAdapter
        }


        if (jsonString != "nouser"){
            getUserTournaments()
        }


        list.setOnItemClickListener { parent, view, position, id ->
            if (EDIT){
                Toast.makeText(this, "You Clicked at " +tournamentsName[+ position], Toast.LENGTH_SHORT).show();
                val intent = intent.setClassName(this,"com.example.d1.tournament.TournamentActivity")
                //can pass any data
                intent.putExtra("user",jsonString)
                intent.putExtra("token",TOKEN)
                intent.putExtra("edit","EDIT")
                if(!tournamentsName[+ position].contains("]")){
                    intent.putExtra("tId","1")
                }else{
                    var a = tournamentsName.get(+position).split("[","]")
                    var id = a.get(1).toInt()
                    print("$a====================================")
                    intent.putExtra("tId","$id")
                }

                startActivity(intent)
                finish()
            }else{
                println("------------------------")
                Toast.makeText(this, "You Clicked at " +tournamentsName[+ position], Toast.LENGTH_SHORT).show();
                val intent = intent.setClassName(this,"com.example.d1.tournament.TournamentActivity")
                //can pass any data
                intent.putExtra("user",jsonString)
                intent.putExtra("token",TOKEN)
                if(!tournamentsName[+ position].contains("]")){
                    intent.putExtra("tId","1")
                }else{
                    var a = tournamentsName.get(+position).split("[","]")
                    var id = a.get(1).toInt()
                    print("$a====================================")
                    intent.putExtra("tId","$id")
                }

                startActivity(intent)
                finish()
            }
        }

    }


    override fun onBackPressed() {
        val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
        if (drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }


    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        // Handle navigation view item clicks here.
        when (item.itemId) {
            R.id.nav_home -> {
                clearStatsAdapter()
                EDIT = false

                //set list view visible
                listView(true)
                runOnUiThread{

                tournamentsName.clear()
                imageId.clear()
                var tournamentsName1 = arrayListOf("Valentine's Day Lead-Off of the World Tournament",
                    "By the Beach Labor Day 1st Down Tournament","Push the button again, I dare you.","Epic Last Day of School Back of the Net Tournament")

                var imageId1 = arrayListOf(R.drawable.tournament,R.drawable.tournament,R.drawable.tournament,R.drawable.tournament)

                tournamentsName.addAll(tournamentsName1)
                imageId.addAll(imageId1)


                    var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                    val list = findViewById<ListView>(R.id.list)
                    listAdapter.notifyDataSetChanged()
                    list.adapter = listAdapter
                }

            }
            R.id.nav_notification -> {
                //set list view invisible
                listView(false)

                clearStatsAdapter()
                //textMessage.setText(R.string.menu_notification)

                EDIT = false
            }
            R.id.nav_history -> {
                clearStatsAdapter()
                EDIT = false

                //set list view visible
                listView(true)
                runOnUiThread{

                tournamentsName.clear()
                imageId.clear()


                    var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                    val list = findViewById<ListView>(R.id.list)
                    listAdapter.notifyDataSetChanged()
                    list.adapter = listAdapter
                }

//                for (i in Tournament_user_have){
//                    getTournament(i)
//                }
                getUserTournaments()
            }
            R.id.nav_edit_tournament -> {
                EDIT = true
                clearStatsAdapter()

                //set list view visible
                listView(true)
                runOnUiThread{

                    tournamentsName.clear()
                    imageId.clear()


                    var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                    val list = findViewById<ListView>(R.id.list)
                    listAdapter.notifyDataSetChanged()
                    list.adapter = listAdapter
                }

//                for (i in Tournament_user_have){
//                    getTournament(i)
//                }
                getUserTournaments()



            }
            R.id.nav_stats -> {
                EDIT = false
                //clear screen
                runOnUiThread{


                    tournamentsName.clear()
                    imageId.clear()


                    var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                    val list = findViewById<ListView>(R.id.list)
                    listAdapter.notifyDataSetChanged()
                    list.adapter = listAdapter
                }

                //set list view invisible
                listView(false)

                //read all stats
                getStats()
            }
            R.id.nav_createTournament -> {

                var gson=Gson();
                var userString = gson.toJson(user)
                val intent = intent.setClassName(this,"com.example.d1.tournament.CreateTournamentActivity")
                intent.putExtra("user",jsonString)
                intent.putExtra("token",TOKEN)
                //intent.putExtra("tId",TournamentId.toString())
                startActivityForResult(intent,0)
                finish()
            }
            R.id.nav_logout ->{
                clearStatsAdapter()

                //set list view visible
                listView(true)

                resetHeader("Sign in","")
                val navView: NavigationView = findViewById(R.id.nav_view)
                var menu = navView.menu
                var nav_cTournament = menu.findItem(R.id.nav_createTournament)
                var nav_history = menu.findItem(R.id.nav_history)
                var nav_logout = menu.findItem(R.id.nav_logout)
                var nav_stats = menu.findItem(R.id.nav_stats)
                var nav_edit_tournament = menu.findItem(R.id.nav_edit_tournament)
                nav_cTournament.setVisible(false)
                nav_history.setVisible(false)
                nav_logout.setVisible(false)
                nav_stats.setVisible(false)
                nav_edit_tournament.setVisible(false)
                logOut()
                LOG_IN = false
                jsonString = "nouser"
                user = null

                EDIT = false

            }
        }
        val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
        drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    //works， got no idea why this version is working
    //after clicking go to a login page
    fun onLogin(v:View){
        if (!LOG_IN){
            //var layout:LinearLayout = v.findViewById(R.id.before_login_in)
            val intent = this.intent.setClassName(this,"com.example.d1.login.LoginActivity")
            //can pass any data
            //intent.putExtra()
            startActivity(intent)
            finish()
        }

    }

    //reset the header to default
    fun resetHeader(n:String,e:String){
        var navigationView = findViewById<NavigationView>(R.id.nav_view)
        var header = navigationView.getHeaderView(0)
        var username = header.findViewById<TextView>(R.id.username_nav)
        var email = header.findViewById<TextView>(R.id.email_nav)


        // var username_nav = LayoutInflater.from(this).inflate(R.layout.nav_header_main,null).findViewById<TextView>(R.id.username_nav)
        // var email_nav = LayoutInflater.from(this).inflate(R.layout.nav_header_main,null).findViewById<TextView>(R.id.email_nav)


        //name to empty string
        username.text = n

        //email to empty string
        email.text = e
    }


    private fun getTournament(id: Int) {

        val request = Request.Builder()
            .url(requestURL+"tournament/"+ "$id")
            .build()


        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    //     var text = findViewById<TextView>(R.id.name)
                    val json = JSONObject(response.body!!.string())

                    var name = json["name"] as String

                    runOnUiThread{
                        tournamentsName.add("[${json["id"]}]"+name)
                        imageId.add(R.drawable.tournament)


                        var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                        val list = findViewById<ListView>(R.id.list)
                        listAdapter.notifyDataSetChanged()
                        list.adapter = listAdapter
                    }

                    println("=========================================")
                    //  text.text = "Response: "+json + "   "+ brackets.javaClass.name

                }
            }
        })
    }

    private fun getUserTournaments(){
        var gson = Gson()
        var user = gson.fromJson(jsonString,User::class.java)

        var request = Request.Builder()
            .url(requestURL+"user/${user.id}/tournaments/")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    //     var text = findViewById<TextView>(R.id.name)
                    val json = JSONArray(response.body!!.string())
                    for (i in 0 until json.length()){
                        println("-------- ${json.getJSONObject(i)["id"]} -----------")
                        getTournament(json.getJSONObject(i)["id"] as Int);
                    }

                }
            }
        })
    }

    private fun getStats(){
        var gson = Gson()
        var user = gson.fromJson(jsonString,User::class.java)

        var request = Request.Builder()
            .url(requestURL+"user/${user.id}/winsandlosses")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    //     var text = findViewById<TextView>(R.id.name)
                    val json = JSONArray(response.body!!.string())

                    for (i in 0 until json.length()){
                        var losses = json.getJSONObject(i)["Losses"] as Int
                        var user = json.getJSONObject(i)["User"] as Int
                        var wins = json.getJSONObject(i)["Wins"] as Int



                        lossesList.add(losses.toString())
                        //userList.add(user.toString())
                        winsList.add(wins.toString())

                        getUser(user)
                    }


//                    runOnUiThread{
//                        var statsAdapter = StatsList(this@MainActivity,lossesList,userList,winsList)
//                        val list = findViewById<ListView>(R.id.stats_list)
//                        list.visibility = View.VISIBLE
//                        statsAdapter.notifyDataSetChanged()
//                        list.adapter = statsAdapter
//                    }
                }
            }
        })
    }


    private fun clearStatsAdapter(){
        var lossesList = arrayListOf<String>()
        var userList = arrayListOf<String>()
        var winsList = arrayListOf<String>()
        var statsAdapter = StatsList(this@MainActivity,lossesList,userList,winsList)
        runOnUiThread{
            val list = findViewById<ListView>(R.id.stats_list)
            statsAdapter.notifyDataSetChanged()
            list.adapter = statsAdapter
            list.visibility = View.INVISIBLE
        }

    }

    private fun listView(b:Boolean){
        val list = findViewById<ListView>(R.id.list)
        if(b){
            list.visibility = View.VISIBLE
        }else{
            list.visibility = View.INVISIBLE
        }
    }

    private fun getUser(id:Int){
        var gson = Gson()
        var user = gson.fromJson(jsonString,User::class.java)

        var request = Request.Builder()
            .url(requestURL+"user/$id")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    //     var text = findViewById<TextView>(R.id.name)
                    val json = response.body!!.string()
                    var gson = Gson()
                    var user = gson.fromJson(json,User::class.java)

                    runOnUiThread{
                        userList.add(user.username)

                        println(winsList)

                        var statsAdapter = StatsList(this@MainActivity,lossesList,userList,winsList)
                        val list = findViewById<ListView>(R.id.stats_list)
                        list.visibility = View.VISIBLE
                        statsAdapter.notifyDataSetChanged()
                        list.adapter = statsAdapter
                    }
                }
            }
        })
    }

    fun logOut(){
        var client = OkHttpClient()

        val credential = Credentials.basic(TOKEN, "unused")

        val request = Request.Builder()
            .url(requestURL+"logout")
            .header("Authorization",credential)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("==============FAIL==========")
                e.printStackTrace()

            }

            //http response
            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) throw IOException("Unexpected code $response")
                    println(response.body!!.string()+"------------------")

                }
            }
        })
    }
}


