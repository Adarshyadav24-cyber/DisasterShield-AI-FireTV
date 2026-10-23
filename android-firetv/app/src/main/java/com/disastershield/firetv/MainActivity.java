package com.disastershield.firetv;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * DisasterShield AI - Fire TV Host Activity
 * Embeds the 10-foot TV HTML5 application inside a hardware-accelerated
 * Fire OS / Android TV WebView with full D-pad remote pass-through.
 */
public class MainActivity extends Activity {

    private WebView mWebView;
    // Default local service URL or production hosted endpoint
    private static final String APP_URL = "http://10.0.2.2:8000/"; // 10.0.2.2 maps to host localhost in Android Emulator

    @Override
    @SuppressLint("SetJavaScriptEnabled")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Keep TV screen awake during emergency monitoring
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideSystemUI();

        mWebView = new WebView(this);
        setContentView(mWebView);

        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        mWebView.setWebViewClient(new WebViewClient());
        mWebView.setWebChromeClient(new WebChromeClient());
        mWebView.setFocusable(true);
        mWebView.setFocusableInTouchMode(true);

        mWebView.loadUrl(APP_URL);
    }

    private void hideSystemUI() {
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Forward TV remote navigation keys directly to spatial navigation engine
        switch (keyCode) {
            case KeyEvent.KEYCODE_DPAD_UP:
            case KeyEvent.KEYCODE_DPAD_DOWN:
            case KeyEvent.KEYCODE_DPAD_LEFT:
            case KeyEvent.KEYCODE_DPAD_RIGHT:
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_ENTER:
                return mWebView.onKeyDown(keyCode, event);
            case KeyEvent.KEYCODE_BACK:
                if (mWebView.canGoBack()) {
                    mWebView.goBack();
                    return true;
                }
                break;
        }
        return super.onKeyDown(keyCode, event);
    }
}
