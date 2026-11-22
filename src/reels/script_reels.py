# -*- coding: utf-8 -*-
"""Reels (9:16, <= 60 s) version: fast second-person summary of the long video."""
from script import Line, Pause, Scene

G = 0.18  # short gap between lines -> reels pace

REEL_SCENES = [
    Scene("r_hook", "title", [
        Line("NR", "300 Spartalıdan biri olsaydın, hayatın tam olarak böyle geçerdi.",
             say="Üç yüz Spartalıdan biri olsaydın, hayatın tam olarak böyle geçerdi.", gap=0.25),
    ], lead=0.25, tail=0.05),
    Scene("r_birth", "training", [
        Line("NR", "Doğar doğmaz yaşlılar seni incelerdi. Zayıf görünseydin, şansın yoktu.", gap=G),
    ], lead=0.05, tail=0.05),
    Scene("r_agoge", "training", [
        Line("NR", "Yedi yaşında annenden alınır, yalınayak ve aç bırakılarak eğitilirdin.", gap=G),
    ], lead=0.05, tail=0.05),
    Scene("r_steal", "training", [
        Line("NR", "Yemeğini çalman beklenirdi. Ama yakalanırsan...", gap=0.1, tag="caught"),
        Pause(1.0, tag="bonk"),
    ], lead=0.05, tail=0.05),
    Scene("r_xerxes", "persian", [
        Line("NR", "M.Ö. 480. Pers Kralı Kserkses, dev bir orduyla geldi.",
             say="Milattan önce dört yüz seksen. Pers Kralı Kserkses, dev bir orduyla geldi.", gap=G),
    ], lead=0.05, tail=0.05),
    Scene("r_pass", "battle", [
        Line("NR", "Kral Leonidas 300 Spartalıyla Termopil Geçidi'ni tuttu.",
             say="Kral Leonidas, üç yüz Spartalıyla Termopil geçidini tuttu.", gap=0.1),
        Line("NR", "Yanlarında yaklaşık 7000 Yunan daha vardı.",
             say="Yanlarında yaklaşık yedi bin Yunan daha vardı.", gap=G, tag="7000"),
    ], lead=0.05, tail=0.05),
    Scene("r_molon", "battle", [
        Line("NR", "Persler: Silahlarınızı bırakın! Leonidas'ın cevabı...", gap=0.15),
        Line("LEO", "Gel de al!", gap=0.45, tag="molon"),
    ], lead=0.05, tail=0.05),
    Scene("r_battle", "battle", [
        Line("NR", "İki gün boyunca, dalga dalga gelen Persleri dar geçitte durdurdunuz.", gap=G),
    ], lead=0.05, tail=0.05),
    Scene("r_betray", "night", [
        Line("NR", "Ama hain Efialtes, dağdaki gizli patikayı Perslere gösterdi.", gap=G),
    ], lead=0.05, tail=0.05),
    Scene("r_last", "solemn", [
        Line("NR", "Üçüncü gün kuşatıldınız. Kaçmadınız. Son nefesinize kadar savaştınız.",
             gap=0.5, tag="last"),
        Pause(1.4, tag="fall"),
    ], lead=0.05, tail=0.05),
    Scene("r_cta", "outro", [
        Line("NR", "Sen olsaydın kalır mıydın? Yorumlara yaz.", gap=0.15, tag="q"),
        Line("NR", "Zaman Kırığı'nı takip et.", gap=0.8, tag="follow"),
    ], lead=0.05, tail=0.0),
]
