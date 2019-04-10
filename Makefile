APK=bin/baccm-0.1-debug.apk
SOURCE=main.py
KV=companycommander.kv
BUILDOZER=buildozer.spec

$(APK): $(SOURCE) $(KV) $(BUILDOZER)
	buildozer android debug

deploy: $(APK)
	cp $(APK) ~/Sync
