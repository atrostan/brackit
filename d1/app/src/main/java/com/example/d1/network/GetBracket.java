package com.example.d1.network;

import android.os.Build;

import androidx.annotation.RequiresApi;

import java.io.IOException;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class GetBracket {
    OkHttpClient client = new OkHttpClient();


    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    public String run(String url) throws IOException {
        Request request = new Request.Builder()
                .url(url)
                .build();

        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
}
