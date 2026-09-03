package com.seungjae.dangifreepass;

import android.accessibilityservice.AccessibilityService;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.SystemClock;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.Toast;

import java.util.List;

public final class FreePassAccessibilityService extends AccessibilityService {
    private static final String TARGET_PACKAGE = "com.stn.mobile_player";
    private static final String PREFS = "freepass_shortcut";
    private static final String ARMED_UNTIL = "armed_until";
    private static final long ACTIVE_WINDOW_MS = 45_000L;
    private static final long CLICK_GUARD_MS = 750L;

    private long lastClickUptime;

    static void arm(Context context) {
        context.getSharedPreferences(PREFS, MODE_PRIVATE)
                .edit()
                .putLong(ARMED_UNTIL, System.currentTimeMillis() + ACTIVE_WINDOW_MS)
                .apply();
    }

    static void disarm(Context context) {
        context.getSharedPreferences(PREFS, MODE_PRIVATE)
                .edit()
                .remove(ARMED_UNTIL)
                .apply();
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (!isArmed() || event == null) {
            return;
        }

        CharSequence eventPackage = event.getPackageName();
        if (eventPackage == null || !TARGET_PACKAGE.contentEquals(eventPackage)) {
            return;
        }

        long now = SystemClock.uptimeMillis();
        if (now - lastClickUptime < CLICK_GUARD_MS) {
            return;
        }

        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (root == null) {
            return;
        }

        if (clickAny(root, "프리패스", "프리 패스")) {
            lastClickUptime = now;
            disarm(this);
            Toast.makeText(this, "프리패스로 이동했어요.", Toast.LENGTH_SHORT).show();
            return;
        }

        if (clickAny(root, "내 강의실", "내강의실")) {
            lastClickUptime = now;
        }
    }

    @Override
    public void onInterrupt() {
        disarm(this);
    }

    private boolean isArmed() {
        SharedPreferences preferences = getSharedPreferences(PREFS, MODE_PRIVATE);
        long until = preferences.getLong(ARMED_UNTIL, 0L);
        if (until <= System.currentTimeMillis()) {
            if (until != 0L) {
                disarm(this);
            }
            return false;
        }
        return true;
    }

    private boolean clickAny(AccessibilityNodeInfo root, String... labels) {
        for (String label : labels) {
            List<AccessibilityNodeInfo> matches = root.findAccessibilityNodeInfosByText(label);
            if (matches == null) {
                continue;
            }
            for (AccessibilityNodeInfo match : matches) {
                AccessibilityNodeInfo candidate = match;
                for (int depth = 0; candidate != null && depth < 7; depth++) {
                    if (candidate.isVisibleToUser()
                            && candidate.isEnabled()
                            && candidate.isClickable()
                            && candidate.performAction(AccessibilityNodeInfo.ACTION_CLICK)) {
                        return true;
                    }
                    candidate = candidate.getParent();
                }
            }
        }
        return false;
    }
}
