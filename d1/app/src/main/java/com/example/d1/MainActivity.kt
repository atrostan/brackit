package com.example.d1

import android.content.Context
import android.content.Intent
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
import com.example.d1.dao.User
import com.example.d1.login.LoginActivity
import org.json.JSONObject
import com.google.gson.Gson


class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {
    private var LOG_IN = false
    lateinit var user:User
    var jsonString = "nouser"

    private lateinit var list: ListView;
    var web = arrayListOf<String>("Java",
        "C++",
        "C#",
        "HTML",
        "CSS")
    var imageId = arrayListOf(R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera,
        R.drawable.ic_menu_camera)

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
            R.id.navigation_notifications -> {
                textMessage.setText(R.string.title_profile)
                return@OnNavigationItemSelectedListener true
            }
        }
        false
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val toolbar: Toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)

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


        var listAdapter = HomeList(this@MainActivity, web, imageId)
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
                nav_cTournament.setVisible(true)
            }


            //userchange(user)
        }

        list.setOnItemClickListener { parent, view, position, id ->
            println("------------------------")
            Toast.makeText(this, "You Clicked at " +web[+ position], Toast.LENGTH_SHORT).show();
            val intent = intent.setClassName(this,"com.example.d1.tournament.TournamentActivity")
            //can pass any data
            intent.putExtra("user",jsonString)
            startActivity(intent)
            finish()
        }

    }

    //after user login, set user info and functions
    fun userchange(user:User){
        var userName = findViewById<TextView>(R.id.login)
        userName.text = user.username

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
                textMessage.setText(R.string.title_home)
            }
            R.id.nav_notification -> {
                textMessage.setText(R.string.menu_notification)
            }
            R.id.nav_history -> {
                textMessage.setText(R.string.menu_history)
            }
            R.id.nav_createTournament -> {
                textMessage.setText(R.string.create_tournament)
                var gson=Gson();
                var userString = gson.toJson(user)
                val intent = intent.setClassName(this,"com.example.d1.tournament.CreateTournamentActivity")
                intent.putExtra("json",userString)
                startActivityForResult(intent,0)
               // finish()
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

        //        layout.setOnClickListener { v ->
//            System.out.println("-----------------------------Befor Login in------------------------------")
//            var t: TextView = v!!.findViewById(R.id.login)
//            t.text = "newText"
//
//            val intent = this.intent.setClassName(this,"com.example.d1.login.LoginActivity")
//            //can pass any data
//            //intent.putExtra()
//            startActivity(intent)
//            finish()
//        }

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
}


