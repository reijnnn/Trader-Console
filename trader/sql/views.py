from flask import render_template, flash, request, Blueprint, current_app
from flask_login import login_required

from sqlalchemy import desc, or_

from ..extensions        import login_manager, csrf, db, logger
from ..user.decorators   import *
from ..utils.pagination  import Pagination

sql_bp = Blueprint('sql', __name__, template_folder='templates')

@sql_bp.route('/execute_sql', defaults={'page': 1})
@sql_bp.route('/execute_sql/<int:page>')
@login_required
@is_super_admin
def execute_sql(page):

   table_list = []
   for model_class in db.Model._decl_class_registry.values():
      if isinstance(model_class, type) and issubclass(model_class, db.Model):
         table_list.append(model_class.__tablename__)

   if request.args.get('sql'):
      sql_text = request.args.get('sql')
      sql_text_formatted = sql_text.strip().lower()

      try:
         if sql_text_formatted.startswith('select'):
            cnt_sql_text = 'select count(1) as total_count, {}'.format(sql_text[len('select'):])
            cursor       = db.session.execute(cnt_sql_text)
            sql_result   = cursor.fetchone()
            total_count  = sql_result['total_count']

            lof_sql_text = '{} limit {} offset {}'.format(sql_text, current_app.config['PAGINATION_PAGE_SIZE'], (page - 1) * current_app.config['PAGINATION_PAGE_SIZE'])
            cursor       = db.session.execute(lof_sql_text)
            sql_columns  = cursor.keys()
            sql_result   = cursor.fetchall()

            pagination = Pagination(page=page,
                                    per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                                    total_count=total_count,
                                    filter_text=sql_text)

            return render_template('execute_sql.html',
                                   sql_columns=sql_columns,
                                   sql_result=sql_result,
                                   sql_text=sql_text,
                                   pagination=pagination,
                                   table_list=table_list)
         elif sql_text_formatted.startswith('update'):
            cursor = db.session.execute(sql_text)
            db.session.commit()

            flash('Updated {} rows'.format(cursor.rowcount), 'success')
         elif sql_text_formatted.startswith('delete'):
            cursor = db.session.execute(sql_text)
            db.session.commit()

            flash('Deleted {} rows'.format(cursor.rowcount), 'success')
         elif sql_text_formatted.startswith('insert'):
            cursor = db.session.execute(sql_text)
            db.session.commit()

            flash('Done', 'success')
         else:
            flash('Unsupported operation', 'warning')

         return render_template('execute_sql.html', sql_text=sql_text, table_list=table_list)
      except Exception as e:
         err = str(e)
         err = err[:err.find('Background on this error') - 1].strip()

         flash(err, 'danger')
         return render_template('execute_sql.html', sql_text=sql_text, table_list=table_list)

   return render_template('execute_sql.html', table_list=table_list)
