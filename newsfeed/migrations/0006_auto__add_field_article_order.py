# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Article.order'
        db.add_column('newsfeed_article', 'order',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Article.order'
        db.delete_column('newsfeed_article', 'order')


    models = {
        'newsfeed.article': {
            'Meta': {'ordering': "['order', '-created_at']", 'object_name': 'Article'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'edited_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '8'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'text': ('ckeditor.fields.RichTextField', [], {'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'newsfeed.featuredsection': {
            'Meta': {'object_name': 'FeaturedSection'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'a_+'", 'null': 'True', 'to': "orm['newsfeed.Article']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'fr'", 'max_length': '8'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['newsfeed']
