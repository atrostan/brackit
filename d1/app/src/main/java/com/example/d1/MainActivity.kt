package com.example.d1

import android.content.Context
import android.content.Intent
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.view.LayoutInflater
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
import android.widget.LinearLayout
import com.android.volley.toolbox.JsonObjectRequest
import com.example.d1.dao.Tournament
import com.example.d1.dao.User
import com.example.d1.login.LoginActivity
import org.json.JSONObject
import com.google.gson.Gson
import okhttp3.*
import java.io.IOException


class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {
    val requestURL = "http://192.168.0.33:5000/api/"
    var client = OkHttpClient()
    private var LOG_IN = false
    lateinit var user:User
    var jsonString = "nouser"
    var TournamentId = 0
    var Tournament_user_have = arrayListOf<Int>()



    var t1 = Tournament(arrayListOf("Patrycja","Cheyenne","Jolene","Roxy"), arrayListOf(1,2,3,4),"Valentine's Day Lead-Off of the World Tournament")
    var t2 = Tournament(arrayListOf("Katie","Needham","Fox","Findlay"), arrayListOf(1,2,3,4),"By the Beach Labor Day 1st Down Tournament")
    var t3 = Tournament(arrayListOf("Roxy","Dunkley","Kofi","Erickson"), arrayListOf(1,2,3,4),"Push the button again, I dare you.")
    var t4 = Tournament(arrayListOf("Patrycja","Cheyenne"), arrayListOf(3,4),"Epic Last Day of School Back of the Net Tournament")

    var tournamentsName = arrayListOf("Valentine's Day Lead-Off of the World Tournament",
        "By the Beach Labor Day 1st Down Tournament","Push the button again, I dare you.","Epic Last Day of School Back of the Net Tournament")

    var imageId = arrayListOf(R.drawable.tournament,R.drawable.tournament,R.drawable.tournament,R.drawable.tournament)
    private lateinit var list: ListView

    /*
    *
    * R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera
        *
        * */



    var date = arrayListOf("date1","date2")
    var score = arrayListOf("score1","score2")
    var u1 = arrayListOf(1,2)
    var u2 = arrayListOf(3,4)


        //when the bottom tab selected
    private lateinit var textMessage: TextView
    private val onNavigationItemSelectedListener = BottomNavigationView.OnNavigationItemSelectedListener { item ->
        when (item.itemId) {
            R.id.navigation_home -> {
                textMessage.setText(R.string.title_home)
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

        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT

        //reset header
        resetHeader("Sign in","")

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


        var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
        val list = findViewById<ListView>(R.id.list)
        list.adapter = listAdapter




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
                resetHeader(user.username,user.email)
                //set create tournament visible
                var menu = navView.menu
                var nav_cTournament = menu.findItem(R.id.nav_createTournament)
                var nav_history = menu.findItem(R.id.nav_history)
                var nav_logout = menu.findItem(R.id.nav_logout)
                nav_cTournament.setVisible(true)
                nav_history.setVisible(true)
                nav_logout.setVisible(true)
            }

        }

        if (intent.hasExtra("tId")){
            var a = intent.getStringExtra("tId")
            TournamentId = a.toInt()
            println("-------------$a-----------------tId in mainactivity")
            Tournament_user_have.add(TournamentId)
            getTournament(TournamentId)
        }

        list.setOnItemClickListener { parent, view, position, id ->
            println("------------------------")
            Toast.makeText(this, "You Clicked at " +tournamentsName[+ position], Toast.LENGTH_SHORT).show();
            val intent = intent.setClassName(this,"com.example.d1.tournament.TournamentActivity")
            //can pass any data
            intent.putExtra("user",jsonString)
            startActivity(intent)
            finish()
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

                for (i in Tournament_user_have){
                    getTournament(i)
                }


            }
            R.id.nav_notification -> {
                textMessage.setText(R.string.menu_notification)
            }
            R.id.nav_history -> {
                tournamentsName.clear()
                imageId.clear()

                var listAdapter = HomeList(this@MainActivity, tournamentsName, imageId)
                val list = findViewById<ListView>(R.id.list)
                listAdapter.notifyDataSetChanged()
                list.adapter = listAdapter

                for (i in Tournament_user_have){
                    getTournament(i)
                }
            }
            R.id.nav_createTournament -> {
                var gson=Gson();
                var userString = gson.toJson(user)
                val intent = intent.setClassName(this,"com.example.d1.tournament.CreateTournamentActivity")
                intent.putExtra("user",jsonString)
                intent.putExtra("tId",TournamentId.toString())
                startActivityForResult(intent,0)
                finish()
            }
            R.id.nav_logout ->{
                resetHeader("Sign in","")
                val navView: NavigationView = findViewById(R.id.nav_view)
                var menu = navView.menu
                var nav_cTournament = menu.findItem(R.id.nav_createTournament)
                var nav_history = menu.findItem(R.id.nav_history)
                var nav_logout = menu.findItem(R.id.nav_logout)
                nav_cTournament.setVisible(false)
                nav_history.setVisible(false)
                nav_logout.setVisible(false)
                LOG_IN = false

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
           // finish()
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

                    tournamentsName.add(name)
                    imageId.add(R.drawable.tournament)

                    runOnUiThread{
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
}


