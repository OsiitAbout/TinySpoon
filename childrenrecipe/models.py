#!/usr/bin/env Python
# coding=utf-8
from __future__ import unicode_literals

from django.db import models
# Create your models here.


class Recipe(models.Model):
	create_time = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=200)
	user = models.CharField(max_length=40, blank=True)
	exihibitpic = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d', blank=False)
	introduce = models.TextField(blank=False)
	tips = models.TextField(blank=True)
	tag = models.ManyToManyField('Tag')

	def __unicode__(self):
		return self.name


class Material(models.Model):
	recipe = models.ForeignKey('Recipe')
	name = models.CharField(max_length=200)
	portion = models.CharField(max_length=20)

	def __unicode__(self):
		return '%s %s' % (self.recipe.name, self.name)


class Procedure(models.Model):
	recipe = models.ForeignKey('Recipe')
	seq = models.IntegerField()
	describe = models.TextField(blank=False)
	image = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d',blank=True)
	create_time = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.recipe.name


class Tag(models.Model):
	name = models.CharField(max_length=100)
	category = models.ForeignKey('Category')
	seq = models.IntegerField()

	def __unicode__(self):
		return self.name


class Category(models.Model):
	name = models.CharField(max_length=100)
	is_tag =models.IntegerField(blank=False)
	seq = models.IntegerField()

	def __unicode__(self):
		return self.name


class Recommend(models.Model):
	create_time = models.DateTimeField(auto_now=True)
	recipe = models.ForeignKey('Recipe')
	name = models.CharField(max_length=200, blank=True)
	introduce = models.TextField(blank=True)
	image = models.ImageField(upload_to='exhibited_picture/%Y/%m/%d', blank=False)
	pubdate = models.DateTimeField()

	def __unicode__(self):
		return self.recipe.name
