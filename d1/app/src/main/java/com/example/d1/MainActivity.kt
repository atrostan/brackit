package com.example.d1

import android.content.Intent
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
import android.widget.LinearLayout
import com.example.d1.login.LoginActivity


class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

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

        list.setOnItemClickListener { parent, view, position, id ->
            Toast.makeText(this, "You Clicked at " +web[+ position], Toast.LENGTH_SHORT).show();
        }

//        val factory:LayoutInflater= layoutInflater;
//        var v1:View = factory.inflate(nav_header_before_login_main,null)
//        onLogin(v1)
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
        }
        val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
        drawerLayout.closeDrawer(GravityCompat.START)
        return true
    }

    //works， got no idea why this version is working
    //after clicking go to a login page
    fun onLogin(v:View){
        var layout:LinearLayout = v.findViewById(R.id.before_login_in)

        layout.setOnClickListener { v ->
            System.out.println("-----------------------------Befor Login in------------------------------")
            var t: TextView = v!!.findViewById(R.id.login)
            t.text = "newText"

            val intent = intent.setClassName(this,"com.example.d1.login.LoginActivity")
            //can pass any data
            //intent.putExtra()
            startActivity(intent)
            finish()
        }

    }
}

