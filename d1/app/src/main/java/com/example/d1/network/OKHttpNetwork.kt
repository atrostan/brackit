package com.example.d1.network

interface OKHttpNetwork {
    fun onSuccess(body: String?)
    fun onFailure()
}